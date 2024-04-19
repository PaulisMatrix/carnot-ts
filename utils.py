from typing import Union, List
from datetime import datetime

from models import DeviceInfo


def convert_to_secs(iso_datetime_str: str) -> Union[float, None]:
    try:
        unix_timestamp = datetime.strptime(
            iso_datetime_str, "%Y-%m-%dT%H:%M:%SZ"
        ).timestamp()
    except:
        # try checking with other format
        unix_timestamp = datetime.strptime(
            iso_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ"
        ).timestamp()

    return unix_timestamp


def convert_to_iso(unix_seconds: float) -> Union[float, None]:
    try:
        iso_datetime_str = datetime.fromtimestamp(unix_seconds).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
    except TypeError:
        return None

    return iso_datetime_str


def parse_redis_resp(device_id: str, response: list) -> List[DeviceInfo]:
    # data format: <device_id> <sts_timestamp> <latitude:longitude,cur_timestamp,speed>
    # redis response format: [(<member>, <score>), (<member>, <score>), ...]
    result: List[DeviceInfo] = []

    member: str
    score: float
    for member, score in response:
        coordinates, timestamp, speed = member.split(",")
        latitude, longitude = list(map(float, coordinates.split(":")))

        device_info = DeviceInfo(
            device_id=device_id,
            device_latitude=latitude,
            device_longitude=longitude,
            device_speed=float(speed),
            timestamp=convert_to_iso(unix_seconds=float(timestamp)),
            sts_timestamp=convert_to_iso(unix_seconds=float(score)),
        )

        result.append(device_info)

    return result
