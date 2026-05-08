from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    HealthCheckResponse,
    MultipleWorkerQuotesResponse,
    WorkerQuote,
    ElectricianQuoteRequest,
    ElectricianQuoteResponse,
    ElectricianSearchResponse,
    SavedQuote,
    QuoteUpdateRequest,
    QuoteResponse
)
from app.services.ai_service import ai_service
from app.services.pricing_service import pricing_service
from app.services.quote_service import quote_service
from app.services.database_service import database_service
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
            customer_email=request.customer_email,
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
                electricianId=quote_data["electricianId"],
                workerName=quote_data["workerName"],
                workerEmail=quote_data["workerEmail"],
                workerLocation=quote_data["workerLocation"],
                workerDescription=quote_data["workerDescription"],
                estimatedHours=quote_data["estimatedHours"],
                hourlyRate=quote_data["hourlyRate"],
                callOutFee=quote_data["callOutFee"],
                labourCost=quote_data["labourCost"],
                emergencyUplift=quote_data["emergencyUplift"],
                minimumCharge=quote_data["minimumCharge"],
                totalQuote=quote_data["totalQuote"],
                jobComplexity=ai_analysis["jobComplexity"],
                matchScore=85.0,
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
            customer_email=request.customer_email,
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
        "emergencyUplift_amount": settings.emergencyUplift,
        "currency": "GBP"
    }

@router.get("/api/v1/debug/worker/{electrician_id}", tags=["Debug"])
async def debug_worker_raw(electrician_id: str):
    """Debug: show raw API response for a worker to check field names"""
    raw = await pricing_service.get_raw_worker_by_id(electrician_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {
        "raw_fields": list(raw.keys()),
        "minimumCharge_raw": raw.get("minimumCharge"),
        "minimum_charge_raw": raw.get("minimum_charge"),
        "minCharge_raw": raw.get("minCharge"),
        "full_raw": raw
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
                    "electricianId": w.electricianId,
                    "name": w.name,
                    "email": w.email,
                    "location": w.location,
                    "description": w.description,
                    "hourlyRate": w.hourlyRate,
                    "callOutFee": w.callOutFee,
                    "minimumCharge": w.minimum_charge,
                    "emergencyUplift_amount": w.emergencyUplift
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


@router.get(
    "/api/v1/electrician/{electrician_id}",
    response_model=ElectricianSearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Electrician"]
)
async def search_electrician(electrician_id: str):
    """
    Search for an electrician by their ID.
    Fetches data directly from the pricing API.
    """
    raw = await pricing_service.get_raw_worker_by_id(electrician_id)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Electrician with ID '{electrician_id}' not found"
        )
    
    return ElectricianSearchResponse(
        electricianId=str(raw.get("electricianId", electrician_id)),
        name=raw.get("name", ""),
        email=raw.get("email", ""),
        location=raw.get("location", ""),
        description=raw.get("description", ""),
        hourlyRate=float(raw.get("hourlyRate", 0)),
        callOutFee=float(raw.get("callOutFee", 0)),
        minimumCharge=float(raw.get("minimumCharge", 0)),
        emergencyUplift_amount=float(raw.get("emergencyUplift", 0)),
        currency=raw.get("currency", "GBP"),
        isActive=raw.get("isActive", False)
    )


@router.post(
    "/api/v1/electrician/{electrician_id}/quote",
    response_model=ElectricianQuoteResponse,
    status_code=status.HTTP_200_OK,
    tags=["Electrician"]
)
async def electrician_self_quote(electrician_id: str, request: ElectricianQuoteRequest):
    """
    Generate a quote for a specific electrician based on a job description.
    The electrician provides a description and gets back a full quote breakdown.
    
    - Fetches the electrician's rates from the pricing API
    - Uses AI to estimate hours and complexity
    - Calculates the full quote using the electrician's own rates
    """
    # Fetch electrician details
    worker = await pricing_service.get_worker_by_id(electrician_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Electrician with ID '{electrician_id}' not found"
        )
    
    # AI analysis
    ai_analysis = ai_service.analyze_job_description(
        job_description=request.job_description,
        is_emergency=request.is_emergency
    )
    
    # Calculate quote using electrician's own rates
    quote_data = quote_service.calculate_quote_for_worker(
        worker=worker,
        estimatedHours=ai_analysis["estimatedHours"],
        is_emergency=request.is_emergency
    )
    
    return ElectricianQuoteResponse(
        electricianId=worker.electricianId,
        electricianName=worker.name,
        electricianEmail=worker.email,
        electricianLocation=worker.location,
        job_description=request.job_description,
        estimatedHours=quote_data["estimatedHours"],
        jobComplexity=ai_analysis["jobComplexity"],
        aiReasoning=ai_analysis["reasoning"],
        callOutFee=quote_data["callOutFee"],
        hourlyRate=quote_data["hourlyRate"],
        labourCost=quote_data["labourCost"],
        emergencyUplift=quote_data["emergencyUplift"],
        minimumCharge=quote_data["minimumCharge"],
        totalQuote=quote_data["totalQuote"],
        priority="emergency" if request.is_emergency else "standard",
        recommendedActions=ai_analysis["recommendedActions"]
    )


# =====================================================
# QUOTE PERSISTENCE ENDPOINTS
# =====================================================

@router.post(
    "/api/v1/quotes/save",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Quote Persistence"]
)
async def save_quote(request: ElectricianQuoteResponse):
    """
    Save a quote to the database for future reference.
    
    This endpoint persists the generated quote so it can be:
    - Retrieved later from the dashboard
    - Confirmed/accepted by the customer
    - Tracked in quote history
    
    Args:
        request: ElectricianQuoteResponse with complete quote details
        
    Returns:
        QuoteResponse: Saved quote with ID and metadata
    """
    try:
        # Check if database is connected
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable. Quote cannot be saved at this time."
            )
        
        # Prepare quote data for persistence
        quote_data = {
            "electricianId": request.electricianId,
            "electricianName": request.electricianName,
            "electricianEmail": request.electricianEmail,
            "job_description": request.job_description,
            "estimatedHours": request.estimatedHours,
            "jobComplexity": request.jobComplexity,
            "callOutFee": request.callOutFee,
            "hourlyRate": request.hourlyRate,
            "labourCost": request.labourCost,
            "emergencyUplift": request.emergencyUplift,
            "minimumCharge": request.minimumCharge,
            "totalQuote": request.totalQuote,
            "isEmergency": request.priority == "emergency",
            "status": "pending",
            "aiReasoning": request.aiReasoning
        }
        
        # Save to database
        quote_id = await database_service.save_quote(quote_data)
        
        # Retrieve the saved quote to return
        saved_quote = await database_service.get_quote_by_id(quote_id)
        
        return saved_quote
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save quote: {str(e)}"
        )


@router.get(
    "/api/v1/quotes/{quote_id}",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    tags=["Quote Persistence"]
)
async def get_quote(quote_id: str):
    """
    Retrieve a specific quote by ID.
    
    Args:
        quote_id: MongoDB quote ID
        
    Returns:
        QuoteResponse: Quote details or 404 if not found
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        quote = await database_service.get_quote_by_id(quote_id)
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote with ID '{quote_id}' not found"
            )
        
        return quote
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quote: {str(e)}"
        )


@router.get(
    "/api/v1/quotes/history/electrician/{electrician_id}",
    response_model=list[QuoteResponse],
    status_code=status.HTTP_200_OK,
    tags=["Quote Persistence"]
)
async def get_electrician_quotes(electrician_id: str):
    """
    Retrieve all quotes for a specific electrician.
    
    Args:
        electrician_id: Electrician ID
        
    Returns:
        list[QuoteResponse]: List of electrician's quotes
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        quotes = await database_service.get_quotes_by_electrician(electrician_id)
        return quotes
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving electrician quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quotes: {str(e)}"
        )


@router.get(
    "/api/v1/quotes/history/customer/{customer_email}",
    response_model=list[QuoteResponse],
    status_code=status.HTTP_200_OK,
    tags=["Quote Persistence"]
)
async def get_customer_quotes(customer_email: str):
    """
    Retrieve all quotes for a specific customer email.
    
    Args:
        customer_email: Customer email address
        
    Returns:
        list[QuoteResponse]: List of customer's quotes
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        quotes = await database_service.get_quotes_by_customer_email(customer_email)
        return quotes
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving customer quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quotes: {str(e)}"
        )


@router.get(
    "/api/v1/quotes",
    response_model=list[QuoteResponse],
    status_code=status.HTTP_200_OK,
    tags=["Quote Persistence"]
)
async def get_all_quotes_list(status_filter: str = None, limit: int = 100):
    """
    Retrieve all saved quotes (optionally filtered by status).
    
    Query Parameters:
        status_filter: Optional status filter (pending/accepted/rejected)
        limit: Maximum number of quotes to return (default 100)
        
    Returns:
        list[QuoteResponse]: List of quotes sorted by creation date (newest first)
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        # Validate status_filter if provided
        if status_filter and status_filter not in ["pending", "accepted", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be one of: pending, accepted, rejected"
            )
        
        quotes = await database_service.get_all_quotes(status=status_filter, limit=limit)
        return quotes
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quotes: {str(e)}"
        )


@router.patch(
    "/api/v1/quotes/{quote_id}/status",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    tags=["Quote Persistence"]
)
async def update_quote_status(quote_id: str, request: QuoteUpdateRequest):
    """
    Update the status of a saved quote (accept/reject).
    
    Args:
        quote_id: MongoDB quote ID
        request: QuoteUpdateRequest with new status and optional notes
        
    Returns:
        QuoteResponse: Updated quote or 404 if not found
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        updated_quote = await database_service.update_quote_status(
            quote_id=quote_id,
            status=request.status,
            notes=request.notes
        )
        
        if not updated_quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote with ID '{quote_id}' not found"
            )
        
        return updated_quote
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating quote status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update quote status: {str(e)}"
        )


@router.delete(
    "/api/v1/quotes/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Quote Persistence"]
)
async def delete_quote_endpoint(quote_id: str):
    """
    Delete a saved quote.
    
    Args:
        quote_id: MongoDB quote ID
        
    Returns:
        204 No Content on success, 404 if not found
    """
    try:
        if not database_service.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection unavailable"
            )
        
        deleted = await database_service.delete_quote(quote_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote with ID '{quote_id}' not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete quote: {str(e)}"
        )
    )