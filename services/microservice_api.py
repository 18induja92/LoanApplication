"""
FastAPI Microservice for Loan Application Processing
REST API for submitting applications and retrieving decisions
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

from database import DatabaseManager
from config.settings import DATABASE_PATH, API_HOST, API_PORT
from orchestration.langgraph_engine import get_orchestrator
from services.models import (
    LoanApplicationRequest,
    ApplicationStatusResponse,
    DecisionResponse,
    ApplicationStatus,
    Classification
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Loan Approval API",
    description="Multi-Agent Loan Approval System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and orchestrator
db = DatabaseManager(DATABASE_PATH)
orchestrator = get_orchestrator()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("FastAPI Microservice starting")
    logger.info(f"API running on {API_HOST}:{API_PORT}")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Loan Approval System",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/apply", tags=["Applications"], response_model=ApplicationStatusResponse)
async def submit_application(request: LoanApplicationRequest):
    """
    Submit a new loan application

    Request body includes:
    - applicant_id: Unique applicant identifier
    - age: Applicant age (18-100)
    - income: Annual income
    - employment_type: FULL_TIME, PART_TIME, SELF_EMPLOYED
    - credit_score: Credit score (300-850)
    - loan_amount: Requested loan amount
    - tenure_months: Loan tenure in months
    - existing_liabilities: Current debts
    - location: Geographic location
    """
    try:
        # Create application record in database
        application_data = request.model_dump()
        app_id = db.create_application(application_data)

        if not app_id:
            logger.error("Failed to create application in database")
            raise HTTPException(status_code=500, detail="Failed to create application")

        # Update status to processing
        db.update_application_status(app_id, "PROCESSING")

        # Process application through orchestrator (use applicant_id from request, not generated app_id)
        logger.info(f"Processing application {app_id}")
        result = orchestrator.process_application(app_id, application_data, applicant_id=request.applicant_id)

        # Extract decision if available
        decision_data = result.get("decision", {})
        decision_summary = decision_data.get("decision_summary", "")

        # Update application status based on decision
        if result.get("status") == "completed":
            db.update_application_status(app_id, "COMPLETED")
        else:
            db.update_application_status(app_id, "FAILED")

        # Store decision in database
        if decision_data:
            db.create_decision({
                "application_id": app_id,
                "classification": "REVIEW",  # Default, parsed from text
                "risk_score": 0.5,
                "confidence_level": 0.7,
                "reasoning": decision_summary,
                "key_decision_factors": str(["Processed by agents"])
            })

        return ApplicationStatusResponse(
            application_id=app_id,
            status=ApplicationStatus.COMPLETED,
            estimated_completion=datetime.now().isoformat()
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing application: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/status/{application_id}", tags=["Applications"], response_model=ApplicationStatusResponse)
async def get_application_status(application_id: str):
    """
    Get the status of a submitted application

    Parameters:
    - application_id: The application ID returned from /apply
    """
    try:
        app = db.get_application(application_id)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        return ApplicationStatusResponse(
            application_id=application_id,
            status=ApplicationStatus(app.get("status", "PENDING")),
            estimated_completion=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/decision/{application_id}", tags=["Decisions"], response_model=DecisionResponse)
async def get_decision(application_id: str):
    """
    Get the final decision for an application

    Parameters:
    - application_id: The application ID

    Returns decision with classification, risk score, confidence, and reasoning
    """
    try:
        # Get application
        app = db.get_application(application_id)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        # Get decision
        decision = db.get_decision(application_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not yet available")

        return DecisionResponse(
            application_id=application_id,
            classification=Classification(decision.get("classification", "REVIEW")),
            risk_score=float(decision.get("risk_score", 0.5)),
            confidence_level=float(decision.get("confidence_level", 0.7)),
            key_decision_factors=str(decision.get("key_decision_factors", "[]")).split(","),
            reasoning=decision.get("reasoning", "Decision processed"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving decision: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/statistics", tags=["Admin"])
async def get_statistics():
    """Get system statistics"""
    try:
        stats = db.get_statistics()
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Custom general exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
