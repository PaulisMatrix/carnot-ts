from dotenv import load_dotenv
import os
import redis

load_dotenv()


def get_redis_pool() -> redis.ConnectionPool:
    host = os.getenv("REDIS_HOST")
    port = os.getenv("REDIS_PORT")
    db = os.getenv("REDIS_DB")
    password = os.getenv("REDIS_PASSWORD")

    # use connection pooling
    # you don't need to worry about explicitly closing the connection after say every command
    # every connection will be released back to the connection pool
    # ref: https://github.com/redis/redis-py/blob/07fc339b4a4088c1ff052527685ebdde43dfc4be/redis/client.py#L580

    pool = redis.ConnectionPool(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
    )

    return pool
