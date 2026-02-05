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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                
                data = response.json()
                workers = []
                
                for item in data:
                    # Skip inactive workers
                    if not item.get("isActive", False):
                        continue
                    
                    # Convert emergencyUplift from percentage (e.g., 50) to decimal (e.g., 0.50)
                    emergency_uplift_percent = item.get("emergencyUplift", 50)
                    emergency_uplift_decimal = emergency_uplift_percent / 100.0
                    
                    worker = WorkerDetails(
                        name=item.get("name", "Unknown Worker"),
                        email=item.get("email", ""),
                        location=item.get("location", ""),
                        description=item.get("description", ""),
                        hourly_rate=float(item.get("hourlyRate", 100.0)),
                        call_out_fee=float(item.get("callOutFee", 65.0)),
                        minimum_charge=float(item.get("minimumCharge", 65.0)),
                        emergency_uplift=emergency_uplift_decimal
                    )
                    workers.append(worker)
                
                return workers
                
        except httpx.HTTPError as e:
            print(f"HTTP Error fetching pricing data: {str(e)}")
            return self._get_fallback_workers()
        except Exception as e:
            print(f"Error fetching pricing data: {str(e)}")
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
    
    def _get_fallback_workers(self) -> List[WorkerDetails]:
        """
        Provide fallback worker data if API is unavailable
        
        Returns:
            List[WorkerDetails]: Default worker data
        """
        return [
            WorkerDetails(
                name="Default Electrician",
                email="default@wirequote.com",
                location="London",
                description="Experienced electrician available for all types of electrical work",
                hourly_rate=settings.base_hourly_rate,
                call_out_fee=settings.call_out_fee,
                minimum_charge=settings.call_out_fee,
                emergency_uplift=settings.emergency_uplift
            )
        ]

# Create singleton instance
pricing_service = PricingService()