from typing import Any, List, Dict, Union

import uvicorn
from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from cache.redis_client import RedisClient
from utils import convert_to_secs, parse_redis_resp
from models import ErrorResponse, DeviceInfo, DeviceLocation

app = FastAPI(title="carnot-ts")

MAX_PAGE_SIZE = 15
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_NUMBER = 10

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/latest-device-info/",
    response_model=DeviceInfo,
    status_code=status.HTTP_200_OK,
)
async def check_key_cardinality(
    device_id: float, redis_cache: RedisClient = Depends(RedisClient)
) -> Any:
    latest_info = redis_cache.zrange(
        key=device_id, start_idx=-1, end_idx=-1, withscores=True
    )

    if len(latest_info) == 0:
        error_resp = ErrorResponse(
            status=status.HTTP_400_BAD_REQUEST,
            info="invalid device id. cross check the correct device id.",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # parse the responses
    device_info = parse_redis_resp(device_id=device_id, response=latest_info)[0]
    return device_info


@app.get(
    "/location-coordinates/",
    response_model=DeviceLocation,
    status_code=status.HTTP_200_OK,
)
async def check_key_cardinality(
    device_id: float, redis_cache: RedisClient = Depends(RedisClient)
):
    start_location = redis_cache.zrange(
        key=device_id, start_idx=0, end_idx=0, withscores=True
    )
    end_location = redis_cache.zrange(
        key=device_id, start_idx=-1, end_idx=-1, withscores=True
    )

    if len(start_location) == 0 or len(end_location) == 0:
        error_resp = ErrorResponse(
            status=status.HTTP_400_BAD_REQUEST,
            info="invalid device id. cross check the correct device id.",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # parse the responses
    start_loc_info = parse_redis_resp(device_id=device_id, response=start_location)[0]
    end_loc_info = parse_redis_resp(device_id=device_id, response=end_location)[0]

    device_location = DeviceLocation(
        device_id=device_id,
        start_location={
            "latitude": start_loc_info.device_latitude,
            "longitude": start_loc_info.device_longitude,
        },
        end_location={
            "latitude": end_loc_info.device_latitude,
            "longitude": end_loc_info.device_longitude,
        },
    )
    return device_location


@app.get(
    "/location-points/",
    response_model=Dict[str, List[DeviceInfo]],
    status_code=status.HTTP_200_OK,
)
async def check_key_cardinality(
    device_id: float,
    iso_start_time: str,
    iso_end_time: str,
    page_size: Union[int, None] = 0,
    page_number: Union[int, None] = 0,
    redis_cache: RedisClient = Depends(RedisClient),
):
    unix_start_time_secs = convert_to_secs(iso_datetime_str=iso_start_time)
    unix_end_time_secs = convert_to_secs(iso_datetime_str=iso_end_time)

    # validate start and end timestamps
    if (not unix_start_time_secs) or (not unix_end_time_secs):
        error_resp = ErrorResponse(
            status=status.HTTP_400_BAD_REQUEST,
            info="invalid start time or end time. must be a valid iso timestamp str",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # validate page_size and page_number
    if page_size < 0 or page_size > MAX_PAGE_SIZE:
        error_resp = ErrorResponse(
            status=status.HTTP_400_BAD_REQUEST,
            info="page size should be within [0,15] range",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if page_number < 0 or page_number > MAX_PAGE_NUMBER:
        error_resp = ErrorResponse(
            status=status.HTTP_400_BAD_REQUEST,
            info="page number should be within [0,10] range",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # handle defaults
    if page_size == 0:
        page_size = DEFAULT_PAGE_SIZE

    limit = page_size
    offset = page_number * page_size

    location_points = redis_cache.zrangebyscore(
        key=device_id,
        min_score=unix_start_time_secs,
        max_score=unix_end_time_secs,
        withscores=True,
        limit=limit,
        offset=offset,
    )

    if len(location_points) == 0:
        error_resp = ErrorResponse(
            status=status.HTTP_404_NOT_FOUND,
            info="invalid device id or start and end timestamp out of range or no records in given page number.",
        )
        return JSONResponse(
            content=jsonable_encoder(error_resp), status_code=status.HTTP_404_NOT_FOUND
        )

    # parse the responses
    location_info = parse_redis_resp(device_id=device_id, response=location_points)

    return {"device_data": location_info}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=3001)
