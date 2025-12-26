import time
from fastapi import (
        APIRouter,
        Request,
        BackgroundTasks
)
from src.cerebrax.app import register
from src.cerebrax.type_and_module import TIME
from src.cerebrax.type_and_module import (
        ShutdownLaunchItem,
        CannelCountdownItem
)

shutdown_router = APIRouter(
    prefix="/shutdown",
    tags=["shutdown"],
)

# http请求关机的同步方法
def sync_set_exit(wait_for_exit: TIME, server: register.SubServer) -> None:
    if wait_for_exit > 0:
        time.sleep(wait_for_exit)
    server.should_exit = True
    return None

@shutdown_router.post("/launch")
async def launch(item: ShutdownLaunchItem, request: Request, bg: BackgroundTasks):
    try:
        server = request.app.state.server
        _wait_for_exit = item.wait_for_exit
        bg.add_task(sync_set_exit, wait_for_exit=_wait_for_exit, server=server)
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
