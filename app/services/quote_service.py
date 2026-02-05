# from app.config import settings
# from app.models import QuoteBreakdown

# class QuoteService:
#     """Service for calculating quote prices"""
    
#     def __init__(self):
#         self.base_hourly_rate = settings.base_hourly_rate
#         self.emergency_uplift_percent = settings.emergency_uplift
#         self.call_out_fee = settings.call_out_fee
    
#     def calculate_quote(
#         self, 
#         estimated_hours: float, 
#         is_emergency: bool = False
#     ) -> QuoteBreakdown:
#         """
#         Calculate the total quote based on hours and emergency status
        
#         Args:
#             estimated_hours: Estimated hours for the job
#             is_emergency: Whether this is an emergency job
            
#         Returns:
#             QuoteBreakdown: Detailed breakdown of the quote
#         """
        
#         # Calculate labour cost
#         labour_cost = estimated_hours * self.base_hourly_rate
        
#         # Calculate emergency uplift if applicable
#         emergency_uplift = None
#         if is_emergency:
#             emergency_uplift = labour_cost * self.emergency_uplift_percent
        
#         # Calculate total quote
#         total_quote = self.call_out_fee + labour_cost
#         if emergency_uplift:
#             total_quote += emergency_uplift
        
#         return QuoteBreakdown(
#             call_out_fee=round(self.call_out_fee, 2),
#             hourly_rate=round(self.base_hourly_rate, 2),
#             estimated_hours=round(estimated_hours, 1),
#             labour_cost=round(labour_cost, 2),
#             emergency_uplift=round(emergency_uplift, 2) if emergency_uplift else None,
#             total_quote=round(total_quote, 2)
#         )
    
#     def get_price_summary(self, breakdown: QuoteBreakdown) -> dict:
#         """
#         Get a formatted price summary
        
#         Args:
#             breakdown: QuoteBreakdown object
            
#         Returns:
#             dict: Formatted price summary
#         """
#         summary = {
#             "call_out_fee": f"£{breakdown.call_out_fee}",
#             "labour": f"£{breakdown.labour_cost} ({breakdown.estimated_hours}h × £{breakdown.hourly_rate})",
#             "total": f"£{breakdown.total_quote}"
#         }
        
#         if breakdown.emergency_uplift:
#             summary["emergency_uplift"] = f"£{breakdown.emergency_uplift} (50% uplift)"
        
#         return summary

# # Create singleton instance
# quote_service = QuoteService()




from app.config import settings
from app.models import QuoteBreakdown, WorkerDetails

class QuoteService:
    """Service for calculating quote prices"""
    
    def __init__(self):
        self.base_hourly_rate = settings.base_hourly_rate
        self.emergency_uplift_percent = settings.emergency_uplift
        self.call_out_fee = settings.call_out_fee
    
    def calculate_quote_for_worker(
        self,
        worker: WorkerDetails,
        estimated_hours: float,
        is_emergency: bool = False
    ) -> dict:
        """
        Calculate quote for a specific worker
        
        Args:
            worker: WorkerDetails object with worker's rates
            estimated_hours: AI-estimated hours for the job
            is_emergency: Whether this is an emergency job
            
        Returns:
            dict: Complete quote breakdown for this worker
        """
        # Calculate labour cost
        labour_cost = estimated_hours * worker.hourly_rate
        
        # Calculate emergency uplift if applicable
        emergency_uplift = None
        if is_emergency:
            emergency_uplift = labour_cost * worker.emergency_uplift
        
        # Calculate total quote
        total_quote = worker.call_out_fee + labour_cost
        if emergency_uplift:
            total_quote += emergency_uplift
        
        # Check minimum charge
        if total_quote < worker.minimum_charge:
            total_quote = worker.minimum_charge
        
        return {
            "worker_name": worker.name,
            "worker_email": worker.email,
            "worker_location": worker.location,
            "worker_description": worker.description,
            "estimated_hours": round(estimated_hours, 1),
            "hourly_rate": round(worker.hourly_rate, 2),
            "call_out_fee": round(worker.call_out_fee, 2),
            "labour_cost": round(labour_cost, 2),
            "emergency_uplift": round(emergency_uplift, 2) if emergency_uplift else None,
            "total_quote": round(total_quote, 2)
        }
    
    def calculate_quote(
        self, 
        estimated_hours: float, 
        is_emergency: bool = False
    ) -> QuoteBreakdown:
        """
        Calculate the total quote based on hours and emergency status
        (Default/fallback method using settings)
        
        Args:
            estimated_hours: Estimated hours for the job
            is_emergency: Whether this is an emergency job
            
        Returns:
            QuoteBreakdown: Detailed breakdown of the quote
        """
        
        # Calculate labour cost
        labour_cost = estimated_hours * self.base_hourly_rate
        
        # Calculate emergency uplift if applicable
        emergency_uplift = None
        if is_emergency:
            emergency_uplift = labour_cost * self.emergency_uplift_percent
        
        # Calculate total quote
        total_quote = self.call_out_fee + labour_cost
        if emergency_uplift:
            total_quote += emergency_uplift
        
        return QuoteBreakdown(
            call_out_fee=round(self.call_out_fee, 2),
            hourly_rate=round(self.base_hourly_rate, 2),
            estimated_hours=round(estimated_hours, 1),
            labour_cost=round(labour_cost, 2),
            emergency_uplift=round(emergency_uplift, 2) if emergency_uplift else None,
            total_quote=round(total_quote, 2)
        )
    
    def get_price_summary(self, breakdown: QuoteBreakdown) -> dict:
        """
        Get a formatted price summary
        
        Args:
            breakdown: QuoteBreakdown object
            
        Returns:
            dict: Formatted price summary
        """
        summary = {
            "call_out_fee": f"£{breakdown.call_out_fee}",
            "labour": f"£{breakdown.labour_cost} ({breakdown.estimated_hours}h × £{breakdown.hourly_rate})",
            "total": f"£{breakdown.total_quote}"
        }
        
        if breakdown.emergency_uplift:
            summary["emergency_uplift"] = f"£{breakdown.emergency_uplift} (50% uplift)"
        
        return summary

# Create singleton instance
quote_service = QuoteService()