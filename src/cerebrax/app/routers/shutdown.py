import asyncio, typing, time
from fastapi import APIRouter, Request, BackgroundTasks
from src.cerebrax.app import shutdown


shutdown_router = APIRouter(
    prefix='/shutdown',
    tags=['shutdown'],
)

@shutdown_router.post('')
async def shutdown(item: shutdown.ShutdownJsonItem, request: Request, bg: BackgroundTasks):
    try:
        server = request.app.state.server
        _wait_for_exit = item.wait_for_exit
        if _wait_for_exit >= 0:
            bg.add_task(shutdown.sync_set_exit, wait_for_exit=_wait_for_exit, server=server)
            return {"shutdown": True, "timestamp": time.time()}
    except AttributeError:
        return {"shutdown": False, "timestamp": time.time()}


__all__ = [
    "shutdown_router",
]
