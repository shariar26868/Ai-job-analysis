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
            estimatedHours=ai_analysis["estimatedHours"],
            jobComplexity=ai_analysis["jobComplexity"],
            aiReasoning=ai_analysis["reasoning"],
            recommendedActions=ai_analysis["recommendedActions"],
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
                estimatedHours=ai_analysis["estimatedHours"],
                is_emergency=request.is_emergency
            )
            
            worker_quote = WorkerQuote(
                workerName=quote_data["workerName"],
                workerEmail=quote_data["workerEmail"],
                workerLocation=quote_data["workerLocation"],
                workerDescription=quote_data["workerDescription"],
                estimatedHours=quote_data["estimatedHours"],
                hourlyRate=quote_data["hourlyRate"],
                callOutFee=quote_data["callOutFee"],
                labourCost=quote_data["labourCost"],
                emergencyUplift=quote_data["emergencyUplift"],
                totalQuote=quote_data["totalQuote"],
                jobComplexity=ai_analysis["jobComplexity"],
                matchScore=85.0,  # Default match score, can be enhanced later
                recommendedActions=ai_analysis["recommendedActions"]
            )
            worker_quotes.append(worker_quote)
        
        # Step 4: Sort by total price (lowest first)
        worker_quotes.sort(key=lambda x: x.totalQuote)
        
        # Build response
        response = MultipleWorkerQuotesResponse(
            original_description=request.job_description,
            priority="emergency" if request.is_emergency else "standard",
            currency="GBP",
            estimatedHours=ai_analysis["estimatedHours"],
            jobComplexity=ai_analysis["jobComplexity"],
            aiReasoning=ai_analysis["reasoning"],
            worker_quotes=worker_quotes,
            totalWorkers=len(worker_quotes)
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
        "base_hourlyRate": settings.base_hourlyRate,
        "callOutFee": settings.callOutFee,
        "emergencyUplift_percent": settings.emergencyUplift * 100,
        "currency": "GBP"
    }

@router.get("/api/v1/workers", tags=["Workers"])
async def get_all_workers():
    """Get all active workers from the pricing API"""
    try:
        workers = await pricing_service.get_all_workers()
        return {
            "totalWorkers": len(workers),
            "workers": [
                {
                    "name": w.name,
                    "email": w.email,
                    "location": w.location,
                    "description": w.description,
                    "hourlyRate": w.hourlyRate,
                    "callOutFee": w.callOutFee,
                    "minimum_charge": w.minimum_charge,
                    "emergencyUplift_percent": w.emergencyUplift * 100
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