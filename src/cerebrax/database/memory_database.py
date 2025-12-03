import redis, uuid, typing, asyncio
import redis.asyncio as aioredis
from ._model import SyncRedisOptions, AsyncRedisOptions


class RedisHandler:
    def __init__(self,
                 auto_connection: bool = False,
                 redis_id: typing.Optional[str] = None,
                 redis_options: typing.Optional[typing.Dict] = None) -> None:
        """
        默认创建同步的Redis客户端
        :param auto_connection:
        :param redis_options:
        """
        self._redis = None
        self._sync_connections = {}
        self._async_connections = {}
        if auto_connection:
            _redis_options = redis_options if isinstance(redis_options, typing.Dict) else {}
            SyncRedisOptions.model_validate(_redis_options)
            self._redis = redis.Redis(**_redis_options)
            self._redis_id = redis_id or uuid.uuid4().hex
            self._sync_connections[self._redis_id] = self._redis

    @property
    def default_redis(self, return_id: bool = False) -> redis.Redis | tuple[str, redis.Redis] | None:
        if self._redis:
            if return_id:
                return self._redis
            else:
                return self._redis_id, self._redis
        else:
            return None

    @property
    def sync_connections(self) -> typing.Dict[str, redis.Redis]:
        return self._sync_connections

    @property
    def async_connections(self) -> typing.Dict[str, aioredis.Redis]:
        return self._async_connections

    @property
    def connections_lookup(self) -> typing.Set[str]:
        instances = set(self.sync_connections.keys()) | set(self.async_connections.keys())
        return instances

    def new_sync_redis(self, _id: str, _options: typing.Union[str, typing.Dict], /) -> redis.Redis:
        sync_redis = None
        SyncRedisOptions.model_validate(_options)
        if isinstance(_options, dict):
            sync_redis = redis.Redis(**_options)
        if isinstance(_options, str):
            sync_redis = redis.from_url(_options)
        self._sync_connections[_id] = sync_redis
        return sync_redis

    def new_async_redis(self, _id: str, _options: typing.Union[str, typing.Dict], /) -> aioredis.Redis:
        async_redis = None
        AsyncRedisOptions.model_validate(_options)
        if isinstance(_options, dict):
            async_redis = aioredis.Redis(**_options)
        if isinstance(_options, str):
            async_redis = aioredis.from_url(_options)
        self._async_connections[_id] = async_redis
        return async_redis

    def close_sync_redis(self, _id: str, /) -> None:
        if _id in self.sync_connections:
            _redis = self.sync_connections.pop(_id)
            _redis.close()
        return None

    async def close_async_redis(self, _id) -> None:
        if _id in self.async_connections:
            _redis = self.async_connections.pop(_id)
            await _redis.close()
        return None

    async def clear(self) -> None:
        for r in self.sync_connections.values():
            r.close()
        await asyncio.gather(
            *[ar.close for ar in self.async_connections.values()],
            return_exceptions=True
        )
        self._sync_connections.clear()
        self._async_connections.clear()
        return None


__all__ = [
    "RedisHandler",
]
