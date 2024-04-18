from datetime import datetime


def convert_to_secs(iso_datetime_str: str):
    try:
        date_obj = datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        date_obj = datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%SZ")

    unix_timestamp = date_obj.timestamp()
    return unix_timestamp
