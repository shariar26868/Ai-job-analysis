# from pydantic import BaseModel, Field
# from typing import Literal, Optional, List
# from datetime import datetime

# class JobAnalysisRequest(BaseModel):
#     """Request model for job analysis"""
#     job_description: str = Field(
#         ..., 
#         min_length=10,
#         description="Description of the electrical work needed"
#     )
#     is_emergency: bool = Field(
#         default=False,
#         description="Whether this is an emergency job"
#     )
#     customer_email: Optional[str] = Field(
#         default=None,
#         description="Customer email address (optional)"
#     )

# class JobSuggestion(BaseModel):
#     """Individual job suggestion with confidence score"""
#     job_title: str = Field(
#         ...,
#         description="Short title for the job"
#     )
#     job_description: str = Field(
#         ...,
#         description="Matched/refined job description"
#     )
#     estimated_hours: float = Field(
#         ..., 
#         ge=0.5, 
#         le=100,
#         description="Estimated hours to complete"
#     )
#     calculated_price: float = Field(
#         ..., 
#         ge=0,
#         description="Calculated price in GBP"
#     )
#     call_out_fee: float
#     labour_cost: float
#     emergency_uplift: Optional[float] = None
    
#     job_complexity: Literal["simple", "moderate", "complex"]
#     confidence_score: float = Field(
#         ...,
#         ge=0,
#         le=100,
#         description="Confidence/match percentage (0-100)"
#     )
#     match_reason: str = Field(
#         ...,
#         description="Why this suggestion matches"
#     )
#     recommended_actions: List[str] = Field(
#         default_factory=list,
#         description="Recommended actions"
#     )

# class MultipleJobSuggestionsResponse(BaseModel):
#     """Response with multiple job suggestions sorted by confidence"""
#     original_description: str
#     priority: Literal["standard", "emergency"]
#     currency: str = "GBP"
#     suggestions: List[JobSuggestion] = Field(
#         ...,
#         description="List of job suggestions sorted by confidence (highest first)"
#     )
#     total_suggestions: int

# class JobAnalysisResponse(BaseModel):
#     """Response model for job analysis"""
#     job_description: str
#     estimated_hours: float = Field(
#         ..., 
#         ge=0.5, 
#         le=100,
#         description="Estimated hours to complete the job"
#     )
#     calculated_price: float = Field(
#         ..., 
#         ge=0,
#         description="Calculated price in GBP"
#     )
#     priority: Literal["standard", "emergency"] = Field(
#         ...,
#         description="Job priority level"
#     )
#     status: Literal["pending", "accepted", "rejected"] = Field(
#         default="pending",
#         description="Quote status"
#     )
#     currency: str = Field(
#         default="GBP",
#         description="Currency code"
#     )
    
#     # Price breakdown
#     call_out_fee: float = Field(
#         ...,
#         description="Call-out fee"
#     )
#     labour_cost: float = Field(
#         ...,
#         description="Labour cost"
#     )
#     emergency_uplift: Optional[float] = Field(
#         default=None,
#         description="Emergency uplift cost (if applicable)"
#     )
    
#     # AI Analysis
#     ai_reasoning: str = Field(
#         ...,
#         description="AI's reasoning for the estimates"
#     )
#     job_complexity: Literal["simple", "moderate", "complex"] = Field(
#         ...,
#         description="Assessed job complexity"
#     )
#     recommended_actions: list[str] = Field(
#         default_factory=list,
#         description="Recommended actions or considerations"
#     )

# class QuoteBreakdown(BaseModel):
#     """Detailed quote breakdown"""
#     call_out_fee: float
#     hourly_rate: float
#     estimated_hours: float
#     labour_cost: float
#     emergency_uplift: Optional[float] = None
#     total_quote: float

# class HealthCheckResponse(BaseModel):
#     """Health check response"""
#     status: str
#     app_name: str
#     version: str
#     timestamp: datetime




from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class WorkerDetails(BaseModel):
    """Worker/Electrician details"""
    name: str
    email: str
    location: str
    description: str
    hourly_rate: float
    call_out_fee: float
    minimum_charge: float
    emergency_uplift: float  # Percentage (e.g., 0.5 for 50%)

class JobAnalysisRequest(BaseModel):
    """Request model for job analysis"""
    job_description: str = Field(
        ..., 
        min_length=10,
        description="Description of the electrical work needed"
    )
    is_emergency: bool = Field(
        default=False,
        description="Whether this is an emergency job"
    )
    customer_email: Optional[str] = Field(
        default=None,
        description="Customer email address (optional)"
    )

class WorkerQuote(BaseModel):
    """Quote from a specific worker"""
    worker_name: str
    worker_email: str
    worker_location: str
    worker_description: str
    
    estimated_hours: float
    hourly_rate: float
    call_out_fee: float
    labour_cost: float
    emergency_uplift: Optional[float] = None
    total_quote: float
    
    job_complexity: Literal["simple", "moderate", "complex"]
    match_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="How well this worker matches the job (0-100)"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended actions"
    )

class MultipleWorkerQuotesResponse(BaseModel):
    """Response with quotes from multiple workers sorted by best value"""
    original_description: str
    priority: Literal["standard", "emergency"]
    currency: str = "GBP"
    estimated_hours: float
    job_complexity: Literal["simple", "moderate", "complex"]
    ai_reasoning: str
    
    worker_quotes: List[WorkerQuote] = Field(
        ...,
        description="List of worker quotes sorted by total price (lowest first)"
    )
    total_workers: int

class JobSuggestion(BaseModel):
    """Individual job suggestion with confidence score"""
    job_title: str = Field(
        ...,
        description="Short title for the job"
    )
    job_description: str = Field(
        ...,
        description="Matched/refined job description"
    )
    estimated_hours: float = Field(
        ..., 
        ge=0.5, 
        le=100,
        description="Estimated hours to complete"
    )
    calculated_price: float = Field(
        ..., 
        ge=0,
        description="Calculated price in GBP"
    )
    call_out_fee: float
    labour_cost: float
    emergency_uplift: Optional[float] = None
    
    job_complexity: Literal["simple", "moderate", "complex"]
    confidence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence/match percentage (0-100)"
    )
    match_reason: str = Field(
        ...,
        description="Why this suggestion matches"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended actions"
    )

class MultipleJobSuggestionsResponse(BaseModel):
    """Response with multiple job suggestions sorted by confidence"""
    original_description: str
    priority: Literal["standard", "emergency"]
    currency: str = "GBP"
    suggestions: List[JobSuggestion] = Field(
        ...,
        description="List of job suggestions sorted by confidence (highest first)"
    )
    total_suggestions: int

class JobAnalysisResponse(BaseModel):
    """Response model for job analysis - AI estimates only"""
    job_description: str
    estimated_hours: float = Field(
        ..., 
        ge=0.5, 
        le=100,
        description="AI estimated hours to complete the job"
    )
    job_complexity: Literal["simple", "moderate", "complex"] = Field(
        ...,
        description="Assessed job complexity"
    )
    ai_reasoning: str = Field(
        ...,
        description="AI's reasoning for the estimates"
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Recommended actions or considerations"
    )
    priority: Literal["standard", "emergency"] = Field(
        ...,
        description="Job priority level"
    )
    status: Literal["pending", "accepted", "rejected"] = Field(
        default="pending",
        description="Quote status"
    )
    currency: str = Field(
        default="GBP",
        description="Currency code"
    )

class QuoteBreakdown(BaseModel):
    """Detailed quote breakdown"""
    call_out_fee: float
    hourly_rate: float
    estimated_hours: float
    labour_cost: float
    emergency_uplift: Optional[float] = None
    total_quote: float

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    timestamp: datetime