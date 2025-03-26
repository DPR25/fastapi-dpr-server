from fastapi import FastAPI
from routes import sentinel

app = FastAPI(title="DPR API", description="DPR - Arnes Hackaton Server")

# Include routers
app.include_router(sentinel.router, prefix="/sentinel")

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
