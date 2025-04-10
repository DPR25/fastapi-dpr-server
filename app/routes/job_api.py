# Create router
from typing import List
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
import httpx
from sqlalchemy.orm import Session

from config import MODEL_CONFIG, get_db, DPR_SEGMENTATION_HUB_URL
from data_models.job_model import JobModel

router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

class SingleJobRequest(BaseModel):
    model: str
    center: List[float]
    time_interval: List[str]
    resolution: int
    maxcc: float
    stats: bool

# Create a new job
@router.post("/single", status_code=201)
async def create_job(job_request: SingleJobRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Creates a new job after validating with the backend service
    """
    # Generate a unique job_id using UUID
    job_id = str(uuid.uuid4())
    
    # Create a unique S3 path
    unique_id = str(uuid.uuid4())[:8]  # Using first 8 characters of a UUID for brevity
    s3_path = f"{unique_id}_{job_request.model}_{job_request.resolution}"
    
    # First, make a request to the backend service to validate the job
    validate_job(job_request, single=True)

    try:
        async with httpx.AsyncClient() as client:
            # Send the job request to the backend service
            backend_response = await client.post(
                f'{DPR_SEGMENTATION_HUB_URL}/jobs/submit/',
                json={
                    "job_id": job_id,
                    "model": job_request.model,
                    "center": job_request.center,
                    "time_interval": job_request.time_interval,
                    "resolution": job_request.resolution,
                    "maxcc": job_request.maxcc,
                    "stats": job_request.stats,
                    "s3_path": s3_path
                }
            )
            
            # Check if the backend accepted the job
            if backend_response.status_code != 200:
                error_detail = backend_response.json().get("detail", "Unknown error from backend")
                raise HTTPException(status_code=400, detail=f"Backend validation failed: {error_detail}")
            
            # Extract the response data
            backend_data = backend_response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"Error communicating with backend service: {str(exc)}"
        )
    
    
    # Create a new job record
    new_job = JobModel(
        job_id=job_id,
        model=job_request.model,
        center=job_request.center,
        time_interval=job_request.time_interval,
        resolution=job_request.resolution,
        maxcc=job_request.maxcc,
        stats=job_request.stats,
        status="submitted",
        s3_path=s3_path,
        # created_at is set automatically
        queued_at=None,
        finished_at=None,
        batch_job=False
    )
    
    # Add and commit to database
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Return the created job details
    return {
        "s3_path": s3_path,
        "dpr_torch_response": backend_data,
        "created_at": new_job.created_at
    }

class BatchJobRequest(BaseModel):
    model: str
    center: List[float]
    start_date: str
    resolution: int
    maxcc: float
    splits: int
    split_interval: str
    stats: bool

# Create a new job
@router.post("/batch", status_code=201)
async def create_job(job_request: BatchJobRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Creates a new batch job after validating with the backend service
    """
    # Generate a unique job_id using UUID
    job_id = str(uuid.uuid4())
    
    # Create a unique S3 path
    unique_id = str(uuid.uuid4())[:8]  # Using first 8 characters of a UUID for brevity
    s3_path = f"{unique_id}_{job_request.model}_{job_request.resolution}"
    
    # First, make a request to the backend service to validate the job
    validate_job(job_request, single=True)

    try:
        async with httpx.AsyncClient() as client:
            # Send the job request to the backend service

            # Create a new job record
            new_job = JobModel(
                job_id=job_id,
                model=job_request.model,
                center=job_request.center,
                start_date=job_request.start_date,
                resolution=job_request.resolution,
                maxcc=job_request.maxcc,
                stats=job_request.stats,
                status="submitted",
                s3_path=s3_path,
                splits=job_request.splits,
                split_interval=job_request.split_interval,
                # created_at is set automatically
                queued_at=None,
                finished_at=None,
                batch_job=True
            )
            
            # Add and commit to database
            db.add(new_job)
            db.commit()
            db.refresh(new_job)

            backend_response = await client.post(
                f'{DPR_SEGMENTATION_HUB_URL}/jobs/batch-submit/',
                json={
                    "job_id": job_id,
                    "model": job_request.model,
                    "center": job_request.center,
                    "start_date": job_request.start_date,
                    "resolution": job_request.resolution,
                    "maxcc": job_request.maxcc,
                    "stats": job_request.stats,
                    "s3_path": s3_path,
                    "splits": job_request.splits,
                    "split_interval": job_request.split_interval
                }
            )
            
            # Check if the backend accepted the job
            if backend_response.status_code != 200:
                error_detail = backend_response.json().get("detail", "Unknown error from backend")
                raise HTTPException(status_code=400, detail=f"Backend validation failed: {error_detail}")
            
            # Extract the response data
            backend_data = backend_response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503, 
            detail=f"Error communicating with backend service: {str(exc)}"
        )
    
    # Return the created job details
    return {
        "s3_path": s3_path,
        "dpr_torch_response": backend_data,
        "created_at": new_job.created_at
    }


def validate_job(request, single=True):
    """
    Simple job validation.
    """

    if request.model not in MODEL_CONFIG:
        raise HTTPException(
            status_code=400, 
            detail=f"The model specified does not exist. - {request.model}"
        )
    
    if not single and request.split_interval not in ["weekly", "monthly"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Split interval type is incorrectly set. - {request.split_interval}"
        )
    
    if request.maxcc < 0 or request.maxcc > 1:
        raise HTTPException(
            status_code=400, 
            detail=f"Max cloud coverage (maxcc) should be between 0 and 1. - {request.maxcc}"
        )