from sqlalchemy import DateTime, Column, String, Integer, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Define the Jobs table model
class JobModel(Base):
    __tablename__ = "jobs"
    
    job_id = Column(String, primary_key=True)
    model = Column(String, nullable=False)
    center = Column(ARRAY(Float), nullable=False)
    time_interval = Column(ARRAY(String), nullable=True)
    start_date = Column(String, nullable=True)
    resolution = Column(Integer, nullable=False)
    maxcc = Column(Float, nullable=False)
    stats = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    s3_path = Column(String, nullable=False)
    batch_job = Column(Boolean, nullable=False)

    splits = Column(Integer, nullable=True)
    split_interval = Column(String, nullable=True)
    
    # New datetime fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    queued_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)