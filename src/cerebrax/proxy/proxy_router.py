from fastapi import APIRouter, Request, FastAPI, BackgroundTasks
from pydantic import BaseModel
from aiopath import AsyncPath
import logging, uuid
from manager import ProxyManager
from loader import AddonInstanceCreator


logging.getLogger("mitmproxy").setLevel(logging.CRITICAL)

proxy_router = APIRouter(
    prefix='/proxy',
    tags=['proxy'],
)

class LaunchItem(BaseModel):
    launch: bool
    host: str
    port: int

class LandItem(BaseModel):
    land: bool
    thread_id: str

class LoaderItem(BaseModel):
    load_path: str
    thread_id: str
    covering_repetition: bool = True

@proxy_router.post('/launch')
def launch_proxy(request: Request, item: LaunchItem):
    launch = item.launch
    host, port = item.host, item.port
    if launch:
        if not hasattr(request.app.state, 'proxy_thread') or not isinstance(request.app.state.proxy_thread, dict):
            request.app.state.proxy_thread = {}
        thread_id = uuid.uuid4().hex
        proxy_manager = ProxyManager(
            host=host,
            port=port,
        )
        request.app.state.proxy_thread[thread_id] = proxy_manager
        proxy_manager.launch()
        return {
            "message": "Proxy service enabled successfully.",
            "thread_id": thread_id,
        }
    else:
        return {
            "message": "Proxy service activation failed."
        }

@proxy_router.post('/land')
def land_proxy(request: Request, item: LandItem, bt: BackgroundTasks):
    land = item.land
    thread_id = item.thread_id
    if land:
        proxy_thread = {}
        if not hasattr(request.app.state, 'proxy_thread') or request.app.state.proxy_thread is {}:
            return {
                "message": "There is no existing proxy service.",
            }
        else:
            proxy_thread = request.app.state.proxy_thread
        if thread_id not in proxy_thread.keys():
            return {
                "message": f"Cannot find proxy service with ID '{thread_id}'.",
            }
        proxy_manager = proxy_thread[thread_id]
        del proxy_thread[thread_id]
        bt.add_task(proxy_manager.land)
        return {
            "message": f"The proxy service with ID '{thread_id}' has been successfully closed.",
        }
    else:
        return {
            "message": "Proxy service shutdown failed.",
        }

@proxy_router.post('/load')
async def load(request: Request, item: LoaderItem):
    if hasattr(request.app.state, 'proxy_thread'):
        thread_id = item.thread_id
        proxy_thread = request.app.state.proxy_thread
        if thread_id not in proxy_thread.keys():
            return {
                "message": f"Cannot find proxy service with ID {thread_id}."
            }
        load_path = item.load_path
        covering_repetition = item.covering_repetition
        master = proxy_thread[thread_id].master
        addon_manager = master.addons
        lookup_object = addon_manager.lookup
        aic = AddonInstanceCreator(load_path=load_path)
        addons = await aic.create_addons_instances()
        for addon_name, addon in addons.items():
            if addon_name.lower() in lookup_object.keys():
                if covering_repetition:
                    master.addons.remove(lookup_object[addon_name.lower()])
                else:
                    continue
            else:
                continue
        final_addons = [addon for addon in addons.values()]
        addon_manager.add(*final_addons)
        return {
            "message": f"Added plugins {final_addons} to the service with ID {thread_id}."
        }
    else:
        return {
            "message": "There are currently no available proxy services to load the plugin."
        }


@proxy_router.get('/service')
async def proxy_service(request: Request):
    if hasattr(request.app.state, 'proxy_thread'):
        threads = {}
        for thread_id, thread in request.app.state.proxy_thread.items():
            threads[thread_id] = str(thread)
        return threads
    return {}


app = FastAPI()
app.include_router(proxy_router)

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000)