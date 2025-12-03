from fastapi import APIRouter, Request
import typing, pickle, base64
from pydantic import BaseModel


memory_database_router = APIRouter(
    prefix="/memory_database",
    tags=["memory_database"],
)

@memory_database_router.get("/connections_lookup")
async def connections_lookup(request: Request) -> typing.Set[str]:
    try:
        redis_handler = request.app.state.redis_handler
        return redis_handler.connections_lookup
    except AttributeError:
        return set()


@memory_database_router.get("/sync_connections")
async def sync_connections(request: Request) -> typing.Dict:
    try:
        _sync_connections = request.app.state.redis_handler.sync_connections
        _sc = {}
        print(_sync_connections)
        for k, v in _sync_connections.items():
            _sc[k] = base64.b64encode(pickle.dumps(v)).decode(encoding="ascii")
        return _sc
    except AttributeError:
        return {}

@memory_database_router.get("/async_connections")
async def sync_connections(request: Request) -> typing.Dict:
    try:
        _async_connections = request.app.state.redis_handler.async_connections
        _asc = {}
        for k, v in _async_connections.items():
            _asc[k] = base64.b64encode(pickle.dumps(v)).decode(encoding="ascii")
        return _asc
    except AttributeError:
        return {}

class _Item(BaseModel):
    id: str
    options: typing.Dict

@memory_database_router.post("/new_sync_redis")
async def new_sync_redis(request: Request, item: _Item) -> typing.Dict:
    try:
        redis_handler = request.app.state.redis_handler
        redis_handler.new_sync_redis(item.id, item.options)
        return {"message": "ok"}
    except AttributeError:
        return {"message": "error"}

@memory_database_router.post("/new_async_redis")
async def new_sync_redis(request: Request, item: _Item) -> typing.Dict:
    try:
        redis_handler = request.app.state.redis_handler
        await redis_handler.new_async_redis(item.id, item.options)
        return {"message": "ok"}
    except AttributeError:
        return {"message": "error"}

class _Id(BaseModel):
    id: str

@memory_database_router.post("/close_sync_redis")
async def close_sync_redis(request: Request, item: _Id) -> typing.Dict:
    try:
       redis_handler = request.app.state.redis_handler
       redis_handler.close_sync_redis(item.id)
       return {"message": "ok"}
    except AttributeError:
        return {"message": "error"}

@memory_database_router.post("/close_async_redis")
async def close_sync_redis(request: Request, item: _Id) -> typing.Dict:
    try:
       redis_handler = request.app.state.redis_handler
       await redis_handler.close_async_redis(item.id)
       return {"message": "ok"}
    except AttributeError:
        return {"message": "error"}


@memory_database_router.post("/clear")
async def close_sync_redis(request: Request) -> typing.Dict:
    try:
       redis_handler = request.app.state.redis_handler
       await redis_handler.clear()
       return {"message": "ok"}
    except AttributeError:
        return {"message": "error"}

