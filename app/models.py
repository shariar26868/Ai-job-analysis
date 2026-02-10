from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class WorkerDetails(BaseModel):
    """Worker/Electrician details"""
    electricianId: str
    name: str
    email: str
    location: str
    description: str
    hourlyRate: float
    callOutFee: float
    minimum_charge: float
    emergencyUplift: float  # Percentage (e.g., 0.5 for 50%)

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
    electricianId: str
    workerName: str
    workerEmail: str
    workerLocation: str
    workerDescription: str
    
    estimatedHours: float
    hourlyRate: float
    callOutFee: float
    labourCost: float
    emergencyUplift: Optional[float] = None
    totalQuote: float
    
    jobComplexity: Literal["simple", "moderate", "complex"]
    matchScore: float = Field(
        ...,
        ge=0,
        le=100,
        description="How well this worker matches the job (0-100)"
    )
    recommendedActions: List[str] = Field(
        default_factory=list,
        description="Recommended actions"
    )

class MultipleWorkerQuotesResponse(BaseModel):
    """Response with quotes from multiple workers sorted by best value"""
    original_description: str
    priority: Literal["standard", "emergency"]
    currency: str = "GBP"
    estimatedHours: float
    jobComplexity: Literal["simple", "moderate", "complex"]
    aiReasoning: str
    
    worker_quotes: List[WorkerQuote] = Field(
        ...,
        description="List of worker quotes sorted by total price (lowest first)"
    )
    totalWorkers: int

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
    estimatedHours: float = Field(
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
    callOutFee: float
    labourCost: float
    emergencyUplift: Optional[float] = None
    
    jobComplexity: Literal["simple", "moderate", "complex"]
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
    recommendedActions: List[str] = Field(
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
    estimatedHours: float = Field(
        ..., 
        ge=0.5, 
        le=100,
        description="AI estimated hours to complete the job"
    )
    jobComplexity: Literal["simple", "moderate", "complex"] = Field(
        ...,
        description="Assessed job complexity"
    )
    aiReasoning: str = Field(
        ...,
        description="AI's reasoning for the estimates"
    )
    recommendedActions: list[str] = Field(
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
    callOutFee: float
    hourlyRate: float
    estimatedHours: float
    labourCost: float
    emergencyUplift: Optional[float] = None
    totalQuote: float

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    timestamp: datetime