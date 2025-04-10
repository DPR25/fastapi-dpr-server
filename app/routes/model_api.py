from fastapi import APIRouter, HTTPException

from config import MODEL_CONFIG

router = APIRouter(
    prefix="/api/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

# Get list of available models
@router.get("/", response_model=dict)
async def get_models():
    """
    Returns a list of available models that can be used for job requests
    """
    return MODEL_CONFIG

@router.get("/{model_id}")
async def get_model_details(model_id: str):
    """
    Returns detailed information about a specific model
    """
    if model_id not in MODEL_CONFIG:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return MODEL_CONFIG[model_id]