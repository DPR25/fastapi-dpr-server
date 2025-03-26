# SentinelHub - Statistical API

https://apps.sentinel-hub.com/requests-builder/

https://github.com/sentinel-hub/code-snippets/blob/master/statisticalAPI/Statistical%20API%20Requests.ipynb

https://github.com/sentinel-hub/code-snippets/blob/master/statisticalAPI/Statistical%20API%20Visualization.ipynb

Mosaicking - least CC, least cloud coverage

Tile mosaicking - as many scenes as tiles available in interval
Orbit mosaicking - as many orbits

Data mask - figures out which pixels carry no data, some are excluded because they include no data
Sentinel 2 L2A - scene classification mask, multiple the data mask to exclude some pixels
Rid of clouds - lower cloud coverage, will get rid of tiles which have clouds

For every pixel - instead use Process or Batch API

# SentinelHub - Process API

https://www.youtube.com/watch?v=sX3w3Wd3FBw

QGIS, maybe use GeoTIFF

https://github.com/sentinel-hub/sentinelhub-py/blob/master/examples/process_request.ipynb

# SentinelHub - Data fusion

https://www.youtube.com/watch?v=kbw3OyYkbA4

combining Sentinel-1 and Sentinel-2 data

Mosaicking simple - select only the latest pixel sample or the one pixel available
Mosaicking tile - all the available pixels will be selected
Mosaicking orbit - multiple orbits acquired on different dates