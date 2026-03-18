import httpx
from typing import List, Optional
from app.config import settings
from app.models import WorkerDetails

class PricingService:
    """Service for fetching pricing data from external API"""
    
    def __init__(self):
        self.api_url = settings.pricing_api_url
        self.timeout = settings.pricing_api_timeout
    
    async def get_all_workers(self) -> List[WorkerDetails]:
        """
        Fetch all active workers from the pricing API
        
        Returns:
            List[WorkerDetails]: List of all active workers
        """
        try:
            print(f"📡 Fetching workers from: {self.api_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.api_url)
                
                print(f"✅ API Response Status: {response.status_code}")
                
                response.raise_for_status()
                
                # Get the raw response text first to debug
                raw_data = response.text
                print(f"📦 Raw response type: {type(raw_data)}")
                print(f"📦 Raw response preview: {raw_data[:200]}...")
                
                # Parse JSON
                data = response.json()
                print(f"📊 Parsed data type: {type(data)}")
                
                # Handle different response formats
                if isinstance(data, dict):
                    # If response is {"data": [...]} format
                    if "data" in data:
                        data = data["data"]
                    # If response is {"workers": [...]} format
                    elif "workers" in data:
                        data = data["workers"]
                    # If response has other wrapper
                    else:
                        print(f"📋 Response keys: {data.keys()}")
                
                if not isinstance(data, list):
                    print(f"❌ Unexpected data format: {type(data)}")
                    print(f"📄 Full response: {data}")
                    return self._get_fallback_workers()
                
                print(f"📊 Total workers in API response: {len(data)}")
                
                workers = []
                
                for idx, item in enumerate(data):
                    # Debug each item
                    print(f"\n   📌 Item {idx + 1} type: {type(item)}")
                    
                    if not isinstance(item, dict):
                        print(f"   ⚠️ Skipping non-dict item: {item}")
                        continue
                    
                    # Skip inactive workers
                    is_active = item.get("isActive", False)
                    worker_name = item.get("name", "Unknown")
                    print(f"   Worker: {worker_name} - Active: {is_active}")
                    
                    if not is_active:
                        continue
                    
                    # Convert emergencyUplift from percentage (e.g., 50) to decimal (e.g., 0.50)
                    emergencyUplift_percent = item.get("emergencyUplift", 50)
                    emergencyUplift_decimal = emergencyUplift_percent / 100.0
                    
                    # Handle electricianId which can be string or ObjectId
                    electrician_id = item.get("electricianId", "")
                    if isinstance(electrician_id, dict) and "$oid" in electrician_id:
                        electrician_id = electrician_id["$oid"]
                    else:
                        electrician_id = str(electrician_id)
                    
                    print(f"   ✓ Adding worker: {worker_name} (ID: {electrician_id})")
                    
                    worker = WorkerDetails(
                        electricianId=electrician_id,
                        name=item.get("name", "Unknown Worker"),
                        email=item.get("email", ""),
                        location=item.get("location", ""),
                        description=item.get("description", ""),
                        hourlyRate=float(item.get("hourlyRate", 100.0)),
                        callOutFee=float(item.get("callOutFee", 65.0)),
                        minimum_charge=float(item.get("minimumCharge", 65.0)),
                        emergencyUplift=emergencyUplift_decimal
                    )
                    workers.append(worker)
                
                print(f"\n✅ Successfully loaded {len(workers)} active workers")
                return workers
                
        except httpx.HTTPError as e:
            print(f"❌ HTTP Error fetching pricing data: {str(e)}")
            print(f"   Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            return self._get_fallback_workers()
        except Exception as e:
            print(f"❌ Error fetching pricing data: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_workers()
    
    async def get_worker_by_email(self, email: str) -> Optional[WorkerDetails]:
        """
        Fetch a specific worker by email
        
        Args:
            email: Worker's email address
            
        Returns:
            Optional[WorkerDetails]: Worker details or None if not found
        """
        workers = await self.get_all_workers()
        for worker in workers:
            if worker.email.lower() == email.lower():
                return worker
        return None
    
    async def get_worker_by_id(self, electrician_id: str) -> Optional[WorkerDetails]:
        """
        Fetch a specific worker by electricianId directly from the API
        Falls back to searching all workers if direct fetch fails.
        
        Args:
            electrician_id: Worker's electrician ID
            
        Returns:
            Optional[WorkerDetails]: Worker details or None if not found
        """
        try:
            # Build single-worker URL: base URL replace /all with /{id}
            base = self.api_url.rstrip("/")
            if base.endswith("/all"):
                base = base[:-4]
            single_url = f"{base}/{electrician_id}"
            
            print(f"📡 Fetching single worker from: {single_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(single_url)
                response.raise_for_status()
                data = response.json()
            
            # Handle {"success": true, "data": {...}} format
            item = data.get("data", data) if isinstance(data, dict) else data
            
            if not isinstance(item, dict):
                raise ValueError("Unexpected response format")
            
            emergencyUplift_decimal = float(item.get("emergencyUplift", 50)) / 100.0
            
            return WorkerDetails(
                electricianId=str(item.get("electricianId", electrician_id)),
                name=item.get("name", "Unknown"),
                email=item.get("email", ""),
                location=item.get("location", ""),
                description=item.get("description", ""),
                hourlyRate=float(item.get("hourlyRate", 100.0)),
                callOutFee=float(item.get("callOutFee", 65.0)),
                minimum_charge=float(item.get("minimumCharge", 65.0)),
                emergencyUplift=emergencyUplift_decimal
            )
        except Exception as e:
            print(f"⚠️ Direct fetch failed ({e}), falling back to search all workers")
            workers = await self.get_all_workers()
            for worker in workers:
                if worker.electricianId == electrician_id:
                    return worker
            return None
    
    async def get_raw_worker_by_id(self, electrician_id: str) -> Optional[dict]:
        """
        Fetch raw worker data dict by electricianId (for search endpoint)
        """
        try:
            base = self.api_url.rstrip("/")
            if base.endswith("/all"):
                base = base[:-4]
            single_url = f"{base}/{electrician_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(single_url)
                response.raise_for_status()
                data = response.json()
            
            item = data.get("data", data) if isinstance(data, dict) else data
            return item if isinstance(item, dict) else None
        except Exception as e:
            print(f"❌ Error fetching raw worker: {e}")
            return None
    
    def _get_fallback_workers(self) -> List[WorkerDetails]:
        """
        Provide fallback worker data if API is unavailable
        
        Returns:
            List[WorkerDetails]: Default worker data
        """
        return [
            WorkerDetails(
                electricianId="default-001",
                name="Default Electrician",
                email="default@wirequote.com",
                location="London",
                description="Experienced electrician available for all types of electrical work",
                hourlyRate=settings.base_hourlyRate,
                callOutFee=settings.callOutFee,
                minimum_charge=settings.callOutFee,
                emergencyUplift=settings.emergencyUplift
            )
        ]

# Create singleton instance
pricing_service = PricingService()