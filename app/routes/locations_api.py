import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from data_models.job_model import JobModel, JobResponse
from config import get_db, s3_client, DPR_CLIENT_CONFIG, S3_ENDPOINT
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
    responses={404: {"description": "Not found"}},
)

# Endpoint to get all locations
@router.get("/", response_model=List[JobResponse])
async def get_locations(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(JobModel)
    
    if status:
        query = query.filter(JobModel.status == status)

    jobs = query.all()
    if jobs is None:
        raise HTTPException(status_code=404, detail="No locations found.")
    return jobs


# Endpoint to get specific location
@router.get("/{job_id}", response_model=JobResponse)
async def get_location(job_id: str, db: Session = Depends(get_db)):
     # Fetch the job from the database (this is a mock, replace with actual database call)
    job = db.query(JobModel).filter(JobModel.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Location not found")
    
    #s3_path = f"{DPR_CLIENT_CONFIG['bucket_name']}/{job.s3_path}"

    #print(s3_path)

    # Get the S3 files (metadata.json, statistics.json, images)
    metadata, statistics, image_sources = get_s3_files(job.s3_path)

    return JobResponse(
        job_id=job.job_id,
        model=job.model,
        center=job.center,
        time_interval=job.time_interval,
        start_date=job.start_date,
        resolution=job.resolution,
        maxcc=job.maxcc,
        stats=job.stats,
        status=job.status,
        s3_path=job.s3_path,
        batch_job=job.batch_job,
        created_at=job.created_at,
        queued_at=job.queued_at,
        finished_at=job.finished_at,
        metadata=metadata,
        statistics=statistics,
        image_sources=image_sources
    )

def get_s3_files(s3_path: str):
    try:
        # List all files in the specified S3 directory
        response = s3_client.list_objects_v2(Bucket=DPR_CLIENT_CONFIG['bucket_name'], Prefix=f"{s3_path}")

        if 'Contents' not in response:
            return None, None, []

        image_sources = []
        metadata = None
        statistics = None

        # Iterate through all files in the directory
        for obj in response['Contents']:
            key = obj['Key']
            # Check if the file is metadata.json or statistics.json
            if key.endswith("metadata.json"):
                metadata = json.loads(s3_client.get_object(Bucket=DPR_CLIENT_CONFIG['bucket_name'], Key=key)["Body"].read().decode("utf-8"))
            elif key.endswith("statistics.json"):
                statistics = json.loads(s3_client.get_object(Bucket=DPR_CLIENT_CONFIG['bucket_name'], Key=key)["Body"].read().decode("utf-8"))
            else:
                image_sources.append(f"{S3_ENDPOINT}/{DPR_CLIENT_CONFIG['bucket_name']}/{key}")

        return metadata, statistics, image_sources

    except Exception as e:
        print(f"Error accessing S3: {e}")
        return None, None, []