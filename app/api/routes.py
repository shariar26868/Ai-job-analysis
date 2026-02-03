from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models import (
    JobAnalysisRequest, 
    MultipleJobSuggestionsResponse,
    JobSuggestion,
    HealthCheckResponse
)
from app.services.ai_service import ai_service
from app.services.quote_service import quote_service
from app.config import settings

# Create API router
router = APIRouter()

@router.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to WireQuote AI Backend",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now()
    )

@router.post(
    "/api/v1/quick-estimate",
    response_model=MultipleJobSuggestionsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Job Analysis"]
)
async def quick_estimate(request: JobAnalysisRequest):
    """
    Quick estimate with multiple AI-powered job suggestions
    
    Provide job description and get multiple suggestions sorted by confidence.
    Best match appears first (highest confidence score).
    
    Args:
        request: JobAnalysisRequest (only job_description required)
        
    Returns:
        MultipleJobSuggestionsResponse: Multiple job suggestions sorted by confidence
    """
    try:
        # Get multiple AI suggestions
        ai_analysis = ai_service.analyze_job_with_multiple_suggestions(
            job_description=request.job_description,
            is_emergency=request.is_emergency
        )
        
        suggestions_list = []
        
        for suggestion in ai_analysis["suggestions"]:
            # Calculate quote for this suggestion
            quote_breakdown = quote_service.calculate_quote(
                estimated_hours=suggestion["estimated_hours"],
                is_emergency=request.is_emergency
            )
            
            # Create JobSuggestion object
            job_suggestion = JobSuggestion(
                job_title=suggestion["job_title"],
                job_description=suggestion["refined_description"],
                estimated_hours=suggestion["estimated_hours"],
                calculated_price=quote_breakdown.total_quote,
                call_out_fee=quote_breakdown.call_out_fee,
                labour_cost=quote_breakdown.labour_cost,
                emergency_uplift=quote_breakdown.emergency_uplift,
                job_complexity=suggestion["job_complexity"],
                confidence_score=suggestion["confidence_score"],
                match_reason=suggestion["match_reason"],
                recommended_actions=suggestion["recommended_actions"]
            )
            
            suggestions_list.append(job_suggestion)
        
        # Sort by confidence score (highest first) - ALREADY SORTED by AI service but double check
        suggestions_list.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Build response
        response = MultipleJobSuggestionsResponse(
            original_description=request.job_description,
            priority="emergency" if request.is_emergency else "standard",
            currency="GBP",
            suggestions=suggestions_list,
            total_suggestions=len(suggestions_list)
        )
        
        return response
        
    except Exception as e:
        print(f"Error in quick_estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate estimate: {str(e)}"
        )

@router.get("/api/v1/pricing-info", tags=["Information"])
async def get_pricing_info():
    """Get current pricing information"""
    return {
        "base_hourly_rate": settings.base_hourly_rate,
        "call_out_fee": settings.call_out_fee,
        "emergency_uplift_percent": settings.emergency_uplift * 100,
        "currency": "GBP"
    }