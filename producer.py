import pandas as pd

from cache import redis_client


class Worker:
    def __init__(self) -> None:
        self.redis_client = redis_client.RedisClient()
        # how many records/batch to consider
        self.BATCH_SIZE = 20

    def _add_to_redis(self, key: str, mapping: dict) -> None:
        # stored in redis in the format: <device_id> <sts_timestamp> <latitude:longitude,cur_timestamp,speed>
        self.redis_client.zadd(key=key, mapping=mapping)

    def parse_csv(self, file_path: str):
        df = pd.read_csv(file_path)

        # update the dataframe
        df["time_stamp_unix_secs"] = df["time_stamp"].apply(
            lambda x: pd.Timestamp(x).timestamp()
        )
        df["sts_unix_secs"] = df["sts"].apply(lambda x: pd.Timestamp(x).timestamp())
        df = df.drop(["time_stamp", "sts"], axis=1)
        df = df.rename(
            columns={"time_stamp_unix_secs": "time_stamp", "sts_unix_secs": "sts"}
        )
        df.sort_values(by=["sts"], ignore_index=True, inplace=True)

        batch_data = {}

        cur_device_id = None
        cur_timestamp = None
        cur_sts_timestamp = None

        print("start processing...")

        for _, row in df.iterrows():
            cur_device_id = row["device_fk_id"]
            cur_timestamp = row["time_stamp"]
            cur_sts_timestamp = row["sts"]

            # init batch data
            if cur_device_id not in batch_data:
                batch_data[cur_device_id] = {
                    "lat_sum": 0,
                    "lon_sum": 0,
                    "speed_sum": 0,
                    "count": 0,
                }

            # update batch data
            batch_data[cur_device_id]["lat_sum"] += row["latitude"]
            batch_data[cur_device_id]["lon_sum"] += row["longitude"]
            batch_data[cur_device_id]["speed_sum"] += row["speed"]
            batch_data[cur_device_id]["count"] += 1

            # flush the batch data
            if batch_data[cur_device_id]["count"] == self.BATCH_SIZE:
                avg_lat = round(
                    batch_data[cur_device_id]["lat_sum"] / self.BATCH_SIZE, 4
                )
                avg_long = round(
                    batch_data[cur_device_id]["lon_sum"] / self.BATCH_SIZE, 4
                )
                avg_speed = round(
                    batch_data[cur_device_id]["speed_sum"] / self.BATCH_SIZE, 4
                )

                mapping = {
                    f"{avg_lat}:{avg_long},{cur_timestamp},{avg_speed}": cur_sts_timestamp
                }
                self._add_to_redis(key=cur_device_id, mapping=mapping)

                # reset the batch data
                batch_data[cur_device_id] = {
                    "lat_sum": 0,
                    "lon_sum": 0,
                    "speed_sum": 0,
                    "count": 0,
                }

        # process the last batch
        for device_id, data in batch_data.items():
            if data["count"] > 0:
                avg_lat = round(data["lat_sum"] / data["count"], 4)
                avg_long = round(data["lon_sum"] / data["count"], 4)
                avg_speed = round(data["speed_sum"] / data["count"], 4)

                mapping = {
                    f"{avg_lat}:{avg_long},{cur_timestamp},{avg_speed}": cur_sts_timestamp
                }
                self._add_to_redis(key=device_id, mapping=mapping)

        batch_data.clear()
        print("done processing...")


if __name__ == "__main__":
    file_path = "/Users/rushiyadwade/my_repos/test-pip/carnot-ts/carnot.csv"
    worker = Worker()
    worker.parse_csv(file_path=file_path)
