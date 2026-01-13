from src.cerebrax.common_depend import (
    time,
    APIRouter,
    Request,
    BackgroundTasks,
)
from src.cerebrax.app.tools import (
    sync_set_exit,
)
from src.cerebrax._models import (
    ShutdownConfirm,
    CannelCountdown,
)

shutdown_router = APIRouter(
    prefix="/shutdown",
    tags=["shutdown"],
)

@shutdown_router.post("/confirm")
async def confirm(item: ShutdownConfirm, request: Request, bg: BackgroundTasks):
    try:
        server = request.app.state.server
        _wait_for_exit = item.wait_for_exit
        bg.add_task(sync_set_exit, wait_for_exit=_wait_for_exit, server=server)
        return {"shutdown": True, "timestamp": time.time()}
    except AttributeError:
        pass

@shutdown_router.post("/cancel")
async def cancel(request: Request, item: CannelCountdown):
    try:
        if item.cancel_countdown:
            shutdown_task = request.app.state.shared_instance.shutdown_task
            shutdown_task.cancel()
            return {"cancel_countdown": True}
        else:
            return {"cancel_countdown": False}
    except AttributeError:
        pass

__all__ = [
    "shutdown_router",
]
