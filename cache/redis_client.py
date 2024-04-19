from typing import Union
import redis
from cache.pool import get_redis_pool


class RedisClient(object):
    redis_pool = None

    def __init__(self):
        # init the pool
        # share the connection pool between all the redis connection objects
        if RedisClient.redis_pool is None:
            RedisClient.redis_pool = get_redis_pool()

        # max_connections is max number of connections available in a pool.
        # socket_timeout is operation timeout like client connecting to the socket or reading/writing from a socket.
        self.connection = redis.StrictRedis(
            connection_pool=RedisClient.redis_pool,
            max_connections=10,
            socket_timeout=100,
        )
        # set idle connections timeout to 240secs
        # so if a connection is idle for more than 240secs, close it.
        self.connection.config_set(name="timeout", value=240)

    def zadd(self, key: str, mapping: dict) -> None:
        self.connection.zadd(key, mapping=mapping)

    def zrem(self, key: str, value: list) -> None:
        self.connection.zrem(key, *value)

    def zrange(
        self, key: str, start_idx: int, end_idx: int, withscores: bool = False
    ) -> list:
        return self.connection.zrange(
            name=key, start=start_idx, end=end_idx, withscores=withscores
        )

    def zcard(self, key: str) -> int:
        return self.connection.zcard(name=key)

    def zrangebyscore(
        self,
        key: str,
        min_score: Union[float, str],
        max_score: Union[float, str],
        withscores: bool = False,
    ) -> list:
        return self.connection.zrangebyscore(
            name=key, min=min_score, max=max_score, withscores=withscores
        )


if __name__ == "__main__":
    redis_client = RedisClient()
    redis_client.zadd("players", {"player1": 56})
    redis_client.zadd("players", {"player2": 100})
    redis_client.zadd("players", {"player3": 120})

    # redis_client.zrem("players", ["player1", "player2"])
    # output = redis_client.zrangebyscore("players", "-inf", "inf")
    # get the last and first element in the sorted set using index
    last_location = redis_client.zrange(
        key="players", start_idx=-1, end_idx=-1, withscores=True
    )
    first_location = redis_client.zrange(
        key="players", start_idx=0, end_idx=0, withscores=True
    )
