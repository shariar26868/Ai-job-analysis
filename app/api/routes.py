# from fastapi import APIRouter, HTTPException, status
# from datetime import datetime
# from app.models import (
#     JobAnalysisRequest, 
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
#     "/api/v1/quick-estimate",
#     response_model=MultipleJobSuggestionsResponse,
#     status_code=status.HTTP_200_OK,
#     tags=["Job Analysis"]
# )
# async def quick_estimate(request: JobAnalysisRequest):
#     """
#     Quick estimate with multiple AI-powered job suggestions
    
#     Provide job description and get multiple suggestions sorted by confidence.
#     Best match appears first (highest confidence score).
    
#     Args:
#         request: JobAnalysisRequest (only job_description required)
        
#     Returns:
#         MultipleJobSuggestionsResponse: Multiple job suggestions sorted by confidence
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
        
#         # Sort by confidence score (highest first) - ALREADY SORTED by AI service but double check
#         suggestions_list.sort(key=lambda x: x.confidence_score, reverse=True)
        
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
#         print(f"Error in quick_estimate: {str(e)}")
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
    JobAnalysisResponse,
    HealthCheckResponse,
    MultipleWorkerQuotesResponse,
    WorkerQuote
)
from app.services.ai_service import ai_service
from app.services.pricing_service import pricing_service
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
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Job Analysis"]
)
async def quick_estimate(request: JobAnalysisRequest):
    """
    Analyze job description and return AI estimates
    
    AI analyzes the job and returns:
    - Estimated hours needed
    - Job complexity (simple/moderate/complex)
    - AI reasoning
    - Recommended actions
    
    Your backend then uses this data with worker details to calculate prices.
    
    Args:
        request: Job description, emergency flag, optional email
        
    Returns:
        JobAnalysisResponse: AI analysis with time estimates
    """
    try:
        # AI analyzes job and estimates time
        ai_analysis = ai_service.analyze_job_description(
            job_description=request.job_description,
            is_emergency=request.is_emergency
        )
        
        # Build response
        response = JobAnalysisResponse(
            job_description=request.job_description,
            estimated_hours=ai_analysis["estimated_hours"],
            job_complexity=ai_analysis["job_complexity"],
            ai_reasoning=ai_analysis["reasoning"],
            recommended_actions=ai_analysis["recommended_actions"],
            priority="emergency" if request.is_emergency else "standard",
            status="pending",
            currency="GBP"
        )
        
        return response
        
    except Exception as e:
        print(f"Error in quick_estimate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate estimate: {str(e)}"
        )

@router.post(
    "/api/v1/worker-quotes",
    response_model=MultipleWorkerQuotesResponse,
    status_code=status.HTTP_200_OK,
    tags=["Job Analysis"]
)
async def get_worker_quotes(request: JobAnalysisRequest):
    """
    Analyze job and get quotes from all available workers
    
    This endpoint:
    1. Uses AI to analyze the job and estimate hours
    2. Fetches all active workers from the pricing API
    3. Calculates a quote for each worker
    4. Returns all quotes sorted by total price (lowest first)
    
    Args:
        request: Job description, emergency flag, optional email
        
    Returns:
        MultipleWorkerQuotesResponse: Quotes from all workers
    """
    try:
        # Step 1: AI analyzes job and estimates time
        ai_analysis = ai_service.analyze_job_description(
            job_description=request.job_description,
            is_emergency=request.is_emergency
        )
        
        # Step 2: Fetch all active workers
        workers = await pricing_service.get_all_workers()
        
        if not workers:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No workers available at this time"
            )
        
        # Step 3: Calculate quote for each worker
        worker_quotes = []
        for worker in workers:
            quote_data = quote_service.calculate_quote_for_worker(
                worker=worker,
                estimated_hours=ai_analysis["estimated_hours"],
                is_emergency=request.is_emergency
            )
            
            worker_quote = WorkerQuote(
                worker_name=quote_data["worker_name"],
                worker_email=quote_data["worker_email"],
                worker_location=quote_data["worker_location"],
                worker_description=quote_data["worker_description"],
                estimated_hours=quote_data["estimated_hours"],
                hourly_rate=quote_data["hourly_rate"],
                call_out_fee=quote_data["call_out_fee"],
                labour_cost=quote_data["labour_cost"],
                emergency_uplift=quote_data["emergency_uplift"],
                total_quote=quote_data["total_quote"],
                job_complexity=ai_analysis["job_complexity"],
                match_score=85.0,  # Default match score, can be enhanced later
                recommended_actions=ai_analysis["recommended_actions"]
            )
            worker_quotes.append(worker_quote)
        
        # Step 4: Sort by total price (lowest first)
        worker_quotes.sort(key=lambda x: x.total_quote)
        
        # Build response
        response = MultipleWorkerQuotesResponse(
            original_description=request.job_description,
            priority="emergency" if request.is_emergency else "standard",
            currency="GBP",
            estimated_hours=ai_analysis["estimated_hours"],
            job_complexity=ai_analysis["job_complexity"],
            ai_reasoning=ai_analysis["reasoning"],
            worker_quotes=worker_quotes,
            total_workers=len(worker_quotes)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_worker_quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate worker quotes: {str(e)}"
        )

@router.get("/api/v1/pricing-info", tags=["Information"])
async def get_pricing_info():
    """Get current pricing information (for reference only)"""
    return {
        "base_hourly_rate": settings.base_hourly_rate,
        "call_out_fee": settings.call_out_fee,
        "emergency_uplift_percent": settings.emergency_uplift * 100,
        "currency": "GBP"
    }

@router.get("/api/v1/workers", tags=["Workers"])
async def get_all_workers():
    """Get all active workers from the pricing API"""
    try:
        workers = await pricing_service.get_all_workers()
        return {
            "total_workers": len(workers),
            "workers": [
                {
                    "name": w.name,
                    "email": w.email,
                    "location": w.location,
                    "description": w.description,
                    "hourly_rate": w.hourly_rate,
                    "call_out_fee": w.call_out_fee,
                    "minimum_charge": w.minimum_charge,
                    "emergency_uplift_percent": w.emergency_uplift * 100
                }
                for w in workers
            ]
        }
    except Exception as e:
        print(f"Error fetching workers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workers: {str(e)}"
        )