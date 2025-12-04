from fastapi import APIRouter, Request, FastAPI

proxy_router = APIRouter(
    prefix="/proxy",
    tags=["proxy"],
)

@proxy_router.get("/running")
async def running(request: Request):
    try:
        proxy_handler = request.app.state.proxy_handler
        return {"running": proxy_handler.running}
    except AttributeError:
        return {"running": False}

@proxy_router.get("/pid")
async def pid(request: Request):
    try:
        proxy_handler = request.app.state.proxy_handler
        return {"pid": proxy_handler.pid}
    except AttributeError:
        return {"pid": None}

@proxy_router.post("/start")
async def start(request: Request):
    try:
        proxy_handler = request.app.state.proxy_handler
        proxy_handler.start()
        return {"start": True}
    except AttributeError:
        return {"start": False}

@proxy_router.post("/stop")
async def stop(request: Request):
    try:
        proxy_handler = request.app.state.proxy_handler
        proxy_handler.stop()
        return {"stop": True}
    except AttributeError:
        return {"stop": False}

