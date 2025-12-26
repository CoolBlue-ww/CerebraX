"""
Encapsulate the lifecycle function to automate the management of the app's lifecycle.
Read the app's lifetime in the configuration,
wait asynchronously until the dead time is reached, 
and then send a request to the node to release the shutdown signal.
Simultaneously initialize other independent services.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio, typing, httpx
from dataclasses import dataclass
import register
from src.cerebrax.monitor import config
from src.cerebrax.utils.config import ConfigLoader, ConfigParser, load_cfg, reload_cfg
from src.cerebrax.proxy.handler import ProxyHandler
from src.cerebrax.proxy.certificate import CertificateInstaller
from src.cerebrax.type_and_module import TIME

# 自动关闭服务的异步方法
async def async_set_exit(wait_for_exit: TIME, server: register.SubServer) -> None:
    if wait_for_exit > 0:
        await asyncio.sleep(wait_for_exit)
    server.should_exit = True
    return None

# 关机计时器，指有当life_cycle参数大于0的时候才生效
async def countdown(server: register.SubServer, life_cycle: TIME, wait_for_exit: TIME) -> None:
    if life_cycle > 0:
        try:
            await asyncio.sleep(life_cycle)
        except asyncio.CancelledError:
            return None
        else:
            await async_set_exit(wait_for_exit=wait_for_exit, server=server)
    return None

DefaultCfgDir = "/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/utils"
TomlPath = DefaultCfgDir + "/settings.toml"
PyPath = DefaultCfgDir + "settings.py"

@dataclass
class ImplementationClasses(object):
    config_loader: type[ConfigLoader]
    config_parser: type[ConfigParser]
    proxy_handler: type[ProxyHandler]
    certificate_installer: type[CertificateInstaller]

@dataclass
class SharedInstances(object):
    cfg_parser: typing.Optional[ConfigParser] = None
    proxy_handler: typing.Optional[ProxyHandler] = None
    shutdown_task: typing.Optional[asyncio.Task] = None
    server: typing.Optional[register.SubServer] = None
    server_args: typing.Optional[typing.Dict[str, typing.Any]] = None
    async_httpx_client: httpx.AsyncClient = httpx.AsyncClient()  # 内部可复用的异步客户端


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncGenerator:
    cfg_parser = await load_cfg(path=TomlPath)  # 加载配置文件
    shutdown_task = asyncio.create_task(  # 创建定时关闭服务任务
        countdown(
            server=register.server,  # server 对象
            life_cycle=cfg_parser.lifespan_cfg.life_cycle,  # 服务的生命周期
            wait_for_exit=cfg_parser.lifespan_cfg.wait_for_exit,  # 等待退出的时间
        )
    )
    app.state.shared_instances = SharedInstances(
        cfg_parser=cfg_parser,  # 加载解析配置文件
        shutdown_task=shutdown_task,  # 将shutdown task注册到全局对象，用于取消定时关机
        server=register.server,  # 注册server实例
        server_args=register.server_args  # 启动server时的参数
    )
    """
    注册全部的功能实现类
    """
    app.state.implementation_classes = ImplementationClasses(
        config_parser=ConfigParser, # 配置文件解析实现类
        config_loader=ConfigLoader,  # 配置文件加载实现类
        proxy_handler=ProxyHandler,  # 代理控制实现类
        certificate_installer=CertificateInstaller, # 代理证书下载实现类
    )
    config_monitor = cfg.ConfigFileEventMonitor(
        path=DefaultCfgDir,
        name="settings.toml",
        reload=reload_cfg,
        shared_instances=app.state.shared_instances,
    )
    config_monitor.start()  # 开启配置文件监控
    # -------------------------------------------------------------
    yield
    # -------------------------------------------------------------
    await config_monitor.stop()  # 关闭配置文件监控
    try:
        await asyncio.wait_for(
            fut=shutdown_task,  # 等待关机任务
            timeout=cfg_parser.lifespan_cfg.exit_timeout  # 等待超时时间
        )
    except asyncio.TimeoutError:
        pass  # 未到达设置时长手动退出





