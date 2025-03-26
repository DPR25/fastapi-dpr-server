import os
from dotenv import load_dotenv
from sentinelhub import SHConfig, SentinelHubDownloadClient

load_dotenv()

SENTINEL_API_ID = os.getenv("SENTINEL_API_ID", "sentinel_api_id")
SENTINEL_API_SECRET = os.getenv("SENTINEL_API_SECRET", "sentinel_api_secret")

sh_config = SHConfig(
    instance_id='dpr_sentinel',
    sh_client_id=SENTINEL_API_ID,
    sh_client_secret=SENTINEL_API_SECRET,
)

sh_client = SentinelHubDownloadClient(config=sh_config)