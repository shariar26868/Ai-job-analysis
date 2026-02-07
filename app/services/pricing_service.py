# import httpx
# from typing import List, Optional
# from app.config import settings
# from app.models import WorkerDetails

# class PricingService:
#     """Service for fetching pricing data from external API"""
    
#     def __init__(self):
#         self.api_url = settings.pricing_api_url
#         self.timeout = settings.pricing_api_timeout
    
#     async def get_all_workers(self) -> List[WorkerDetails]:
#         """
#         Fetch all active workers from the pricing API
        
#         Returns:
#             List[WorkerDetails]: List of all active workers
#         """
#         try:
#             async with httpx.AsyncClient(timeout=self.timeout) as client:
#                 response = await client.get(self.api_url)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 workers = []
                
#                 for item in data:
#                     # Skip inactive workers
#                     if not item.get("isActive", False):
#                         continue
                    
#                     # Convert emergencyUplift from percentage (e.g., 50) to decimal (e.g., 0.50)
#                     emergencyUplift_percent = item.get("emergencyUplift", 50)
#                     emergencyUplift_decimal = emergencyUplift_percent / 100.0
                    
#                     worker = WorkerDetails(
#                         name=item.get("name", "Unknown Worker"),
#                         email=item.get("email", ""),
#                         location=item.get("location", ""),
#                         description=item.get("description", ""),
#                         hourlyRate=float(item.get("hourlyRate", 100.0)),
#                         callOutFee=float(item.get("callOutFee", 65.0)),
#                         minimum_charge=float(item.get("minimumCharge", 65.0)),
#                         emergencyUplift=emergencyUplift_decimal
#                     )
#                     workers.append(worker)
                
#                 return workers
                
#         except httpx.HTTPError as e:
#             print(f"HTTP Error fetching pricing data: {str(e)}")
#             return self._get_fallback_workers()
#         except Exception as e:
#             print(f"Error fetching pricing data: {str(e)}")
#             return self._get_fallback_workers()
    
#     async def get_worker_by_email(self, email: str) -> Optional[WorkerDetails]:
#         """
#         Fetch a specific worker by email
        
#         Args:
#             email: Worker's email address
            
#         Returns:
#             Optional[WorkerDetails]: Worker details or None if not found
#         """
#         workers = await self.get_all_workers()
#         for worker in workers:
#             if worker.email.lower() == email.lower():
#                 return worker
#         return None
    
#     def _get_fallback_workers(self) -> List[WorkerDetails]:
#         """
#         Provide fallback worker data if API is unavailable
        
#         Returns:
#             List[WorkerDetails]: Default worker data
#         """
#         return [
#             WorkerDetails(
#                 name="Default Electrician",
#                 email="default@wirequote.com",
#                 location="London",
#                 description="Experienced electrician available for all types of electrical work",
#                 hourlyRate=settings.base_hourlyRate,
#                 callOutFee=settings.callOutFee,
#                 minimum_charge=settings.callOutFee,
#                 emergencyUplift=settings.emergencyUplift
#             )
#         ]

# # Create singleton instance
# pricing_service = PricingService()



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
                
                data = response.json()
                print(f"📊 Total workers in API response: {len(data)}")
                
                workers = []
                
                for item in data:
                    # Skip inactive workers
                    is_active = item.get("isActive", False)
                    print(f"   Worker: {item.get('name', 'Unknown')} - Active: {is_active}")
                    
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
                    
                    print(f"   ✓ Adding worker: {item.get('name')} (ID: {electrician_id})")
                    
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
                
                print(f"✅ Successfully loaded {len(workers)} active workers")
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
        Fetch a specific worker by electricianId
        
        Args:
            electrician_id: Worker's electrician ID
            
        Returns:
            Optional[WorkerDetails]: Worker details or None if not found
        """
        workers = await self.get_all_workers()
        for worker in workers:
            if worker.electricianId == electrician_id:
                return worker
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