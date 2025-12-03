import asyncio, typing, time
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from uvicorn import Server


shutdown_router = APIRouter(
    prefix='/shutdown',
    tags=['shutdown'],
)

class Item(BaseModel):
    shutdown: bool = False
    wait: typing.Union[int, float] = 0

def sync_set_exit(wait: typing.Union[int, float], server: typing.Optional[Server]) -> None:
    if wait > 0:
        time.sleep(wait)
    server.should_exit = True
    return None

@shutdown_router.post('')
async def shutdown(item: Item, request: Request, bg: BackgroundTasks):
    _shutdown, _wait = item.shutdown, item.wait
    server = request.app.state.server
    if shutdown and _wait >= 0:
        bg.add_task(sync_set_exit, wait=_wait, server=server)
        message = {'message': '关机成功!', 'timestamp': time.time()}
        return message
    else:
        message = {'message': '关机失败！', 'timestamp': time.time()}
        return message

__all__ = [
    "shutdown_router",
]
