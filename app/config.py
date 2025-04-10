import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import boto3
from botocore.config import Config

from utils import load_json
#from sentinelhub import SHConfig, SentinelHubDownloadClient

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
DPR_SEGMENTATION_HUB_URL = os.getenv("DPR_SEGMENTATION_HUB_URL", "http://localhost:8080")
S3_ENDPOINT = os.getenv("AWS_ENDPOINT", "aws_endpoint")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


s3_client_config = Config(
    request_checksum_calculation="WHEN_REQUIRED",
    response_checksum_validation="WHEN_REQUIRED"
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "aws_access_key_id"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "aws_secret_access_key"),
    endpoint_url=S3_ENDPOINT,
    use_ssl=True,
    config=s3_client_config
)

# Function to initialize database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

MODEL_CONFIG = load_json('model_config.json')

DPR_CLIENT_CONFIG = load_json("dpr_client_config.json")