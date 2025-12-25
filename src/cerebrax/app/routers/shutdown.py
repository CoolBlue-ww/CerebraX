import asyncio, typing, time
from fastapi import (
        APIRouter,
        Request,
        BackgroundTasks
)
from src.cerebrax.app import shutdown_tools
from src.cerebrax.tools.type_and_module import (
        ShutdownLaunchItem,
        CannelCountdownItem
)

shutdown_router = APIRouter(
    prefix="/shutdown",
    tags=["shutdown"],
)

@shutdown_router.post("/launch")
async def launch(item: ShutdownLaunchItem, request: Request, bg: BackgroundTasks):
    try:
        server = request.app.state.server
        _wait_for_exit = item.wait_for_exit
        bg.add_task(shutdown_tools.sync_set_exit, wait_for_exit=_wait_for_exit, server=server)
        return {"shutdown": True, "timestamp": time.time()}
    except AttributeError:
        return {"shutdown": False, "timestamp": time.time()}

@shutdown_router.post("/cancel_countdown")
async def cancel_countdown(request: Request, item: CannelCountdownItem):
    try:
        if item.cancel_countdown:
            shutdown_task = request.app.state.shared_instance.shutdown_task
            shutdown_task.cancel()
            return {"cancel_countdown": True}
        else:
            return {"cancel_countdown": False}
    except AttributeError:
        return {"cancel_countdown": False}

__all__ = [
    "shutdown_router",
]
