import io
from fastapi import APIRouter, Response
from pydantic import BaseModel
from calendar import monthrange

import datetime
import numpy as np
import matplotlib.pyplot as plt

from config import (
    sh_config,
    sh_client
)
from utils import (
    make_bbox_square,
    plot_image,
    save_image,
    encode_image
)

from evalscripts import EvalScripts

from typing import Optional, List, Tuple

from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    bbox_to_dimensions,
    bbox_to_resolution
)

router = APIRouter()

# Pydantic model for input data
class RequestDataSingleImage(BaseModel):
    bbox: list[float, float, float, float]  # (min_long, min_lat, max_long, max_lat)
    time_interval: list[str, str]  # ("YYYY-MM-DD", "YYYY-MM-DD")
    resolution: list[int, int] = [256, 256]  # Default resolution
    maxcc: float = 0.1

@router.get("/single")
def get_image(request_data: RequestDataSingleImage):

    # Extract custom parameters from request body
    bbox_coords = tuple(request_data.bbox)
    resolution = tuple(request_data.resolution)
    time_interval = tuple(request_data.time_interval)
    maxcc = request_data.maxcc

    # Prepare the bounding box in WGS84
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    square_bbox, target_res = make_bbox_square(bbox, width=resolution[0], height=resolution[1])
    size = bbox_to_dimensions(square_bbox, resolution=target_res)

    print(f"Adjusted Square Image Shape: {size} pixels")
    print(f"Custom Image shape at {resolution} m resolution: {size} pixels")

    request_true_color = get_true_color_request(time_interval, square_bbox, size, maxcc)

    true_color_imgs = request_true_color.get_data()[0]
    print(f"Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}.")
    
    img = true_color_imgs["default.tif"]
    norm_factor = true_color_imgs["userdata.json"]["norm_factor"]

    # plot function
    # factor 1/255 to scale between 0-1
    # factor 3.5 to increase brightness
    #save_image(image, "test.png", factor=3.5 / 255, clip_range=(0, 1))
    # Convert the NumPy array to bytes (PNG format)
    image_bytes = encode_image(img, format="png", factor=norm_factor, clip_range=(0, 1))

    return Response(content=image_bytes, media_type="image/png")

# Define Pydantic model for input data
class RequestDataTemporalImages(BaseModel):
    bbox: list[float, float, float, float]  # (min_long, min_lat, max_long, max_lat)
    start_date: str # "YYYY-MM-DD"
    resolution: list[int, int] = [256, 256]  # Default resolution
    maxcc: float = 0.2
    n_chunks: int = 12  # Default to 12 months (can be changed)

@router.get("/temporal")
def get_temporal_images(request_data: RequestDataTemporalImages):

    # Extract custom parameters from request body
    bbox_coords = tuple(request_data.bbox)
    resolution = tuple(request_data.resolution)
    start_date = request_data.start_date
    n_chunks = request_data.n_chunks
    maxcc = request_data.maxcc

    # Prepare the bounding box in WGS84
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    square_bbox, target_res = make_bbox_square(bbox, width=resolution[0], height=resolution[1])
    size = bbox_to_dimensions(square_bbox, resolution=target_res)

    # Extract custom parameters from the request body
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    today = datetime.datetime.today().date().isoformat()

    slots = []
    for i in range(n_chunks):
        # Compute the first day of the month
        first_day = start_date.replace(day=1) - datetime.timedelta(days=30 * i)
        first_day = first_day.replace(day=1)  # Ensure it's the first day
        
        # Compute the last day of the month
        last_day = first_day.replace(day=monthrange(first_day.year, first_day.month)[1])
        
        # If it's the last interval, adjust it to end at `start_date`
        if i == 0:
            slots.append((first_day.isoformat(), start_date.isoformat()))
        else:
            slots.append((first_day.isoformat(), last_day.isoformat()))

    slots = slots[::-1]  # Reverse to maintain chronological order

    print("Monthly time windows:\n")
    for slot in slots:
        print(slot)

    list_of_requests = [get_true_color_request(slot, square_bbox, size, maxcc) for slot in slots]
    list_of_requests = [request.download_list[0] for request in list_of_requests]

    # Download data with multiple threads
    data = sh_client.download(list_of_requests, max_threads=5)

    # Determine grid layout for subplots
    n_images = len(data)
    ncols = min(n_images, 4)  # Max 4 columns
    nrows = (n_images + ncols - 1) // ncols  # Calculate number of rows

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 5 * nrows))

    # Ensure axs is always a 2D array
    axs = np.array(axs).reshape(nrows, ncols)

    # Plot each image in a subplot
    for idx, (data, ax) in enumerate(zip(data, axs.flat)):
        img = data["default.tif"]
        norm_factor = data["userdata.json"]["norm_factor"]
        ax.imshow(np.clip(img * norm_factor, 0, 1))
        ax.set_title(f"{slots[idx][0]} - {slots[idx][1]}", fontsize=10)
        ax.axis("off")

    # Hide any unused subplots
    for ax in axs.flat[idx + 1:]:
        ax.axis("off")

    # Save if needed
    #fig.savefig("test.png", format="png", bbox_inches="tight", pad_inches=0.1)

    # Save the plot to an in-memory buffer
    img_buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(img_buffer, format="png", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

    img_buffer.seek(0)

    return Response(content=img_buffer.getvalue(), media_type="image/png")

def get_true_color_request(time_interval, request_bbox, request_size, maxcc=0.1):
    
    return SentinelHubRequest(
        evalscript=EvalScripts.get_script("TRUE_COLOR"),
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_RECENT,
                maxcc=maxcc
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF),
            SentinelHubRequest.output_response("userdata", MimeType.JSON)
        ],
        bbox=request_bbox,
        size=request_size,
        config=sh_config,
    )