from fastapi import FastAPI
from routes.model_api import router as model_router
from routes.job_api import router as job_router
from routes.locations_api import router as locations_router

description = """
# DPR Zoo Segmentation Job API - Arnes Hackaton Server
"""

app = FastAPI(
    title="DPR Zoo Segmentation Job API",
    description=description,
    version="0.0.1",
    contact={
        "name": "DPR Team"
    },
)

# Include routers
app.include_router(model_router)
app.include_router(job_router)
app.include_router(locations_router)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
