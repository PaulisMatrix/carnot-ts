from typing import Dict
from pydantic import BaseModel


class DeviceInfo(BaseModel):
    device_id: str
    device_latitude: float
    device_longitude: float
    device_speed: float
    timestamp: str
    sts_timestamp: str


class DeviceLocation(BaseModel):
    device_id: str
    start_location: Dict[str, float]
    end_location: Dict[str, float]


class ErrorResponse(BaseModel):
    status: str
    info: str
