# DPR FastAPI server

FastAPI server used as bridge between the backend server for image segmentation jobs ([DPR Zoo Segmentation Hub](https://github.com/DPR25/dpr-zoo-segmentation-hub)) and the actual frontend ([Timber AI](https://github.com/DPR25/front)) of the Timber AI.

## Installation

- [FastAPI](https://fastapi.tiangolo.com/)
- Other python packages listed in `app/requirements.txt`


# Usage

Run with:

```
cd app/
uvicorn main:app --port 8000 --reload
```