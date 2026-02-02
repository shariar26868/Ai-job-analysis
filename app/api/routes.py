# from fastapi import APIRouter, HTTPException, status
# from datetime import datetime
# from app.models import (
#     JobAnalysisRequest, 
#     JobAnalysisResponse,
#     MultipleJobSuggestionsResponse,
#     JobSuggestion,
#     HealthCheckResponse
# )
# from app.services.ai_service import ai_service
# from app.services.quote_service import quote_service
# from app.config import settings

# # Create API router
# router = APIRouter()

# @router.get("/", tags=["Root"])
# async def root():
#     """Root endpoint - API information"""
#     return {
#         "message": "Welcome to WireQuote AI Backend",
#         "version": settings.app_version,
#         "docs": "/docs",
#         "health": "/health"
#     }

# @router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
# async def health_check():
#     """Health check endpoint"""
#     return HealthCheckResponse(
#         status="healthy",
#         app_name=settings.app_name,
#         version=settings.app_version,
#         timestamp=datetime.now()
#     )

# @router.post(
#     "/api/v1/analyze-job-multiple",
#     response_model=MultipleJobSuggestionsResponse,
#     status_code=status.HTTP_200_OK,
#     tags=["Job Analysis"]
# )
# async def analyze_job_multiple(request: JobAnalysisRequest):
#     """
#     Analyze job description and return MULTIPLE AI-powered suggestions
    
#     This endpoint returns multiple possible interpretations of the job,
#     sorted by confidence/match percentage (highest first).
    
#     Perfect for showing users different options based on their description.
    
#     Args:
#         request: JobAnalysisRequest containing job details
        
#     Returns:
#         MultipleJobSuggestionsResponse: Multiple job suggestions with confidence scores
#     """
#     try:
#         # Get multiple AI suggestions
#         ai_analysis = ai_service.analyze_job_with_multiple_suggestions(
#             job_description=request.job_description,
#             is_emergency=request.is_emergency
#         )
        
#         suggestions_list = []
        
#         for suggestion in ai_analysis["suggestions"]:
#             # Calculate quote for this suggestion
#             quote_breakdown = quote_service.calculate_quote(
#                 estimated_hours=suggestion["estimated_hours"],
#                 is_emergency=request.is_emergency
#             )
            
#             # Create JobSuggestion object
#             job_suggestion = JobSuggestion(
#                 job_title=suggestion["job_title"],
#                 job_description=suggestion["refined_description"],
#                 estimated_hours=suggestion["estimated_hours"],
#                 calculated_price=quote_breakdown.total_quote,
#                 call_out_fee=quote_breakdown.call_out_fee,
#                 labour_cost=quote_breakdown.labour_cost,
#                 emergency_uplift=quote_breakdown.emergency_uplift,
#                 job_complexity=suggestion["job_complexity"],
#                 confidence_score=suggestion["confidence_score"],
#                 match_reason=suggestion["match_reason"],
#                 recommended_actions=suggestion["recommended_actions"]
#             )
            
#             suggestions_list.append(job_suggestion)
        
#         # Build response
#         response = MultipleJobSuggestionsResponse(
#             original_description=request.job_description,
#             priority="emergency" if request.is_emergency else "standard",
#             currency="GBP",
#             suggestions=suggestions_list,
#             total_suggestions=len(suggestions_list)
#         )
        
#         return response
        
#     except Exception as e:
#         print(f"Error in analyze_job_multiple: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to analyze job: {str(e)}"
#         )

# @router.post(
#     "/api/v1/analyze-job",
#     response_model=JobAnalysisResponse,
#     status_code=status.HTTP_200_OK,
#     tags=["Job Analysis"]
# )
# async def analyze_job(request: JobAnalysisRequest):
#     """
#     Analyze electrical job description and return AI-powered estimates
    
#     This endpoint:
#     1. Analyzes the job description using OpenAI
#     2. Estimates time required
#     3. Calculates pricing
#     4. Provides recommendations
    
#     Args:
#         request: JobAnalysisRequest containing job details
        
#     Returns:
#         JobAnalysisResponse: Complete analysis with estimates and pricing
#     """
#     try:
#         # Step 1: AI Analysis
#         ai_analysis = ai_service.analyze_job_description(
#             job_description=request.job_description,
#             is_emergency=request.is_emergency
#         )
        
#         # Step 2: Calculate Quote
#         quote_breakdown = quote_service.calculate_quote(
#             estimated_hours=ai_analysis["estimated_hours"],
#             is_emergency=request.is_emergency
#         )
        
#         # Step 3: Determine priority
#         priority = "emergency" if request.is_emergency else "standard"
        
#         # Step 4: Build response
#         response = JobAnalysisResponse(
#             job_description=request.job_description,
#             estimated_hours=ai_analysis["estimated_hours"],
#             calculated_price=quote_breakdown.total_quote,
#             priority=priority,
#             status="pending",
#             currency="GBP",
#             call_out_fee=quote_breakdown.call_out_fee,
#             labour_cost=quote_breakdown.labour_cost,
#             emergency_uplift=quote_breakdown.emergency_uplift,
#             ai_reasoning=ai_analysis["reasoning"],
#             job_complexity=ai_analysis["job_complexity"],
#             recommended_actions=ai_analysis["recommended_actions"]
#         )
        
#         return response
        
#     except Exception as e:
#         print(f"Error in analyze_job: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to analyze job: {str(e)}"
#         )

# @router.post(
#     "/api/v1/quick-estimate",
#     tags=["Job Analysis"]
# )
# async def quick_estimate(
#     job_description: str,
#     is_emergency: bool = False
# ):
#     """
#     Quick estimate endpoint - returns simplified response
    
#     Args:
#         job_description: The electrical work description
#         is_emergency: Whether this is an emergency
        
#     Returns:
#         dict: Quick estimate with basic pricing
#     """
#     try:
#         ai_analysis = ai_service.analyze_job_description(
#             job_description=job_description,
#             is_emergency=is_emergency
#         )
        
#         quote_breakdown = quote_service.calculate_quote(
#             estimated_hours=ai_analysis["estimated_hours"],
#             is_emergency=is_emergency
#         )
        
#         return {
#             "estimated_hours": ai_analysis["estimated_hours"],
#             "estimated_price": quote_breakdown.total_quote,
#             "complexity": ai_analysis["job_complexity"],
#             "currency": "GBP"
#         }
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate estimate: {str(e)}"
#         )

# @router.get("/api/v1/pricing-info", tags=["Information"])
# async def get_pricing_info():
#     """Get current pricing information"""
#     return {
#         "base_hourly_rate": settings.base_hourly_rate,
#         "call_out_fee": settings.call_out_fee,
#         "emergency_uplift_percent": settings.emergency_uplift * 100,
#         "currency": "GBP"
#     }




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