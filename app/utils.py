"""
Utilities used by the server
"""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import cv2

from sentinelhub import (
    CRS,
    BBox,
    bbox_to_dimensions,
    bbox_to_resolution,
    to_utm_bbox
)

def plot_image(
    image: np.ndarray, factor: float = 1.0, clip_range: tuple[float, float] | None = None, **kwargs: Any
) -> None:
    """Utility function for plotting RGB images."""
    _, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])

def save_image(
    image: np.ndarray, 
    file_path: str, 
    factor: float = 1.0, 
    clip_range = None, 
    **kwargs: Any
) -> None:
    """Utility function for saving RGB images to a file."""
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    
    ax.set_xticks([])
    ax.set_yticks([])

    fig.savefig(file_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)  # Close the figure to free memory

def encode_image(
    image: np.ndarray, 
    format: str = "png", 
    factor: float = 1.0, 
    clip_range = None
) -> bytes:
    """Encodes a NumPy array to bytes in the specified format with optional scaling and clipping."""
    
    # Apply factor scaling
    image = image * factor
    
    # Apply clipping if specified
    if clip_range is not None:
        image = np.clip(image, *clip_range)
    
    # Convert to 8-bit format for OpenCV encoding (assuming input is float)
    if image.dtype != np.uint8:
        image = (255 * (image - image.min()) / (image.max() - image.min())).astype(np.uint8)

    if image.shape[-1] == 3:  # Ensure it's a color image
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Encode image to specified format (PNG/JPEG)
    _, buffer = cv2.imencode(f".{format}", image)
    
    return buffer.tobytes()

def make_bbox_square(bbox: BBox, width: int, height: int) -> BBox:
    """Adjusts bbox dimensions to fit the target resolution while keeping the center fixed.
    :param bbox: Input bounding box (WGS84).
    :param width: Target image width in pixels.
    :param height: Target image height in pixels.
    :return: Adjusted bbox in WGS84 that ensures square pixel resolution.
    """
    # Convert bbox to UTM for accurate measurement
    utm_bbox = to_utm_bbox(bbox)
    east1, north1 = utm_bbox.lower_left
    east2, north2 = utm_bbox.upper_right

    # Compute current width and height in meters
    bbox_width_m = abs(east2 - east1)
    bbox_height_m = abs(north2 - north1)

    # Compute per-pixel resolution for width and height
    res_x = bbox_width_m / width
    res_y = bbox_height_m / height

    # Use the larger resolution to make pixels square
    target_res = max(res_x, res_y)

    # Compute new bbox size
    new_width_m = target_res * width
    new_height_m = target_res * height

    # Compute center point
    center_x = (east1 + east2) / 2
    center_y = (north1 + north2) / 2

    # Define new bbox centered around the same point
    new_east1 = center_x - new_width_m / 2
    new_east2 = center_x + new_width_m / 2
    new_north1 = center_y - new_height_m / 2
    new_north2 = center_y + new_height_m / 2

    new_bbox = BBox(bbox=(new_east1, new_north1, new_east2, new_north2), crs=utm_bbox.crs)

    # Convert back to WGS84 for SentinelHub
    return new_bbox.transform(CRS.WGS84), target_res


evalscript_true_color = """
        //VERSION=3

        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"],
                    units: "DN"
                }],
                output: {
                    bands: 3,
                    sampleType: "INT16"
                }
            };
        }
        
        function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
            outputMetadata.userData = { "norm_factor":  inputMetadata.normalizationFactor }
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
"""