from fastapi import FastAPI
from routes.model_api import router as model_router
from routes.job_api import router as job_router

app = FastAPI(title="DPR API", description="DPR - Arnes Hackaton Server")

# Include routers
app.include_router(model_router)
app.include_router(job_router)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
