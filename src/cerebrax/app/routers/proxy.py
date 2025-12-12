"""
Proxy功能对外暴露的接口
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from src.cerebrax.app.routers import util
import typing

proxy_router = APIRouter(
    prefix="/proxy",
    tags=["proxy"],
)

@proxy_router.post("/start")
async def start_proxy(request: Request):
    implementation_classes = util.get_implementation_classes(request=request)
    shared_instances = util.get_shared_instances(request=request)
    proxy_handler = shared_instances.proxy_handler
    if proxy_handler:
        if proxy_handler.running:
            return None
    cfg_parser = shared_instances.cfg_parser
    proxy_handler = implementation_classes.proxy_handler(
        startup_command=cfg_parser.proxy_cfg.startup_command
    )
    request.app.state.shared_instances.proxy_handler = proxy_handler
    proxy_handler.start()
    return None

@proxy_router.post("/stop")
async def stop_proxy(request: Request):
    shared_instances = util.get_shared_instances(request=request)
    if not shared_instances.proxy_handler:
        return None
    proxy_handler = shared_instances.proxy_handler
    if proxy_handler.running:
        await proxy_handler.stop()
    request.app.state.shared_instances.proxy_handler = None
    return None

@proxy_router.post("/restart")
async def restart_proxy(request: Request):
    implementation_classes = util.get_implementation_classes(request=request)
    shared_instances = util.get_shared_instances(request=request)
    proxy_handler = shared_instances.proxy_handler
    if proxy_handler:
        if proxy_handler.running:
            proxy_handler.stop()
    cfg_parser = shared_instances.cfg_parser
    new_proxy_handler = implementation_classes.proxy_handler(
        startup_command=cfg_parser.proxy_cfg.startup_command
    )
    request.app.state.shared_instances.proxy_handler = new_proxy_handler
    new_proxy_handler.start()
    return None

@proxy_router.get("/running")
async def running_proxy(request: Request):
    shared_instance = util.get_shared_instances(request=request)
    proxy_handler = shared_instance.proxy_handler
    if not proxy_handler:
        return False
    else:
        return proxy_handler.running

Platforms = typing.Literal["windows", "linux", "ios", "android", "firefox", "other-platform", "macos"]
OtherPlatformFormat = typing.Literal["pem", "p12"]

class Item(BaseModel):
    proxy: str = "http://localhost:8080"
    platform: typing.Optional[Platforms] = None
    other_platform_format: typing.Optional[OtherPlatformFormat] = None
    save_dir: typing.Optional[str] = None

@proxy_router.post("/certificate")
async def get_cert(request: Request, item: Item):
    implementation_classes = util.get_implementation_classes(request=request)
    shared_instance = util.get_shared_instances(request=request)
    proxy_handler = shared_instance.proxy_handler
    if proxy_handler and proxy_handler.running:
        certificate_installer = implementation_classes.CertificateInstaller(
            proxy=item.proxy
        )
        save_path = await certificate_installer.install(
            platform=item.platform,
            other_platform_format=item.other_platform_format,
            save_dir=item.save_dir,
        )
        return save_path
    return ""
