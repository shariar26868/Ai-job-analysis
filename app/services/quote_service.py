# from app.config import settings
# from app.models import QuoteBreakdown, WorkerDetails

# class QuoteService:
#     """Service for calculating quote prices"""
    
#     def __init__(self):
#         self.base_hourlyRate = settings.base_hourlyRate
#         self.emergencyUplift_percent = settings.emergencyUplift
#         self.callOutFee = settings.callOutFee
    
#     def calculate_quote_for_worker(
#         self,
#         worker: WorkerDetails,
#         estimatedHours: float,
#         is_emergency: bool = False
#     ) -> dict:
#         """
#         Calculate quote for a specific worker
        
#         Args:
#             worker: WorkerDetails object with worker's rates
#             estimatedHours: AI-estimated hours for the job
#             is_emergency: Whether this is an emergency job
            
#         Returns:
#             dict: Complete quote breakdown for this worker
#         """
#         # Calculate labour cost
#         labourCost = estimatedHours * worker.hourlyRate
        
#         # Calculate emergency uplift if applicable
#         emergencyUplift = None
#         if is_emergency:
#             emergencyUplift = labourCost * worker.emergencyUplift
        
#         # Calculate total quote
#         totalQuote = worker.callOutFee + labourCost
#         if emergencyUplift:
#             totalQuote += emergencyUplift
        
#         # Check minimum charge
#         if totalQuote < worker.minimum_charge:
#             totalQuote = worker.minimum_charge
        
#         return {
#             "workerName": worker.name,
#             "workerEmail": worker.email,
#             "workerLocation": worker.location,
#             "workerDescription": worker.description,
#             "estimatedHours": round(estimatedHours, 1),
#             "hourlyRate": round(worker.hourlyRate, 2),
#             "callOutFee": round(worker.callOutFee, 2),
#             "labourCost": round(labourCost, 2),
#             "emergencyUplift": round(emergencyUplift, 2) if emergencyUplift else None,
#             "totalQuote": round(totalQuote, 2)
#         }
    
#     def calculate_quote(
#         self, 
#         estimatedHours: float, 
#         is_emergency: bool = False
#     ) -> QuoteBreakdown:
#         """
#         Calculate the total quote based on hours and emergency status
#         (Default/fallback method using settings)
        
#         Args:
#             estimatedHours: Estimated hours for the job
#             is_emergency: Whether this is an emergency job
            
#         Returns:
#             QuoteBreakdown: Detailed breakdown of the quote
#         """
        
#         # Calculate labour cost
#         labourCost = estimatedHours * self.base_hourlyRate
        
#         # Calculate emergency uplift if applicable
#         emergencyUplift = None
#         if is_emergency:
#             emergencyUplift = labourCost * self.emergencyUplift_percent
        
#         # Calculate total quote
#         totalQuote = self.callOutFee + labourCost
#         if emergencyUplift:
#             totalQuote += emergencyUplift
        
#         return QuoteBreakdown(
#             callOutFee=round(self.callOutFee, 2),
#             hourlyRate=round(self.base_hourlyRate, 2),
#             estimatedHours=round(estimatedHours, 1),
#             labourCost=round(labourCost, 2),
#             emergencyUplift=round(emergencyUplift, 2) if emergencyUplift else None,
#             totalQuote=round(totalQuote, 2)
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
#             "callOutFee": f"£{breakdown.callOutFee}",
#             "labour": f"£{breakdown.labourCost} ({breakdown.estimatedHours}h × £{breakdown.hourlyRate})",
#             "total": f"£{breakdown.totalQuote}"
#         }
        
#         if breakdown.emergencyUplift:
#             summary["emergencyUplift"] = f"£{breakdown.emergencyUplift} (50% uplift)"
        
#         return summary

# # Create singleton instance
# quote_service = QuoteService()




from app.config import settings
from app.models import QuoteBreakdown, WorkerDetails

class QuoteService:
    """Service for calculating quote prices"""
    
    def __init__(self):
        self.base_hourlyRate = settings.base_hourlyRate
        self.emergencyUplift_percent = settings.emergencyUplift
        self.callOutFee = settings.callOutFee
    
    def calculate_quote_for_worker(
        self,
        worker: WorkerDetails,
        estimatedHours: float,
        is_emergency: bool = False
    ) -> dict:
        """
        Calculate quote for a specific worker
        
        Args:
            worker: WorkerDetails object with worker's rates
            estimatedHours: AI-estimated hours for the job
            is_emergency: Whether this is an emergency job
            
        Returns:
            dict: Complete quote breakdown for this worker
        """
        # Calculate labour cost
        labourCost = estimatedHours * worker.hourlyRate
        
        # Calculate emergency uplift if applicable
        emergencyUplift = None
        if is_emergency:
            emergencyUplift = labourCost * worker.emergencyUplift
        
        # Calculate total quote
        totalQuote = worker.callOutFee + labourCost
        if emergencyUplift:
            totalQuote += emergencyUplift
        
        # Check minimum charge
        if totalQuote < worker.minimum_charge:
            totalQuote = worker.minimum_charge
        
        return {
            "electricianId": worker.electricianId,
            "workerName": worker.name,
            "workerEmail": worker.email,
            "workerLocation": worker.location,
            "workerDescription": worker.description,
            "estimatedHours": round(estimatedHours, 1),
            "hourlyRate": round(worker.hourlyRate, 2),
            "callOutFee": round(worker.callOutFee, 2),
            "labourCost": round(labourCost, 2),
            "emergencyUplift": round(emergencyUplift, 2) if emergencyUplift else None,
            "totalQuote": round(totalQuote, 2)
        }
    
    def calculate_quote(
        self, 
        estimatedHours: float, 
        is_emergency: bool = False
    ) -> QuoteBreakdown:
        """
        Calculate the total quote based on hours and emergency status
        (Default/fallback method using settings)
        
        Args:
            estimatedHours: Estimated hours for the job
            is_emergency: Whether this is an emergency job
            
        Returns:
            QuoteBreakdown: Detailed breakdown of the quote
        """
        
        # Calculate labour cost
        labourCost = estimatedHours * self.base_hourlyRate
        
        # Calculate emergency uplift if applicable
        emergencyUplift = None
        if is_emergency:
            emergencyUplift = labourCost * self.emergencyUplift_percent
        
        # Calculate total quote
        totalQuote = self.callOutFee + labourCost
        if emergencyUplift:
            totalQuote += emergencyUplift
        
        return QuoteBreakdown(
            callOutFee=round(self.callOutFee, 2),
            hourlyRate=round(self.base_hourlyRate, 2),
            estimatedHours=round(estimatedHours, 1),
            labourCost=round(labourCost, 2),
            emergencyUplift=round(emergencyUplift, 2) if emergencyUplift else None,
            totalQuote=round(totalQuote, 2)
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
            "callOutFee": f"£{breakdown.callOutFee}",
            "labour": f"£{breakdown.labourCost} ({breakdown.estimatedHours}h × £{breakdown.hourlyRate})",
            "total": f"£{breakdown.totalQuote}"
        }
        
        if breakdown.emergencyUplift:
            summary["emergencyUplift"] = f"£{breakdown.emergencyUplift} (50% uplift)"
        
        return summary

# Create singleton instance
quote_service = QuoteService()