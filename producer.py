import pandas as pd

from cache import redis_client


class Worker:
    def __init__(self) -> None:
        self.redis_client = redis_client.RedisClient()

    def _add_to_redis(self, key: str, mapping: dict) -> None:
        # stored in redis in the format: <device_id> <sts_timestamp> <latitude:longitude,cur_timestamp,speed>
        pass

    def parse_csv(self, file_path: str):
        df = pd.read_csv(file_path)
        print(df.head())


if __name__ == "__main__":
    file_path = "/Users/rushiyadwade/my_repos/test-pip/carnot-ts/carnot.csv"
    worker = Worker()
    worker.parse_csv(file_path=file_path)
