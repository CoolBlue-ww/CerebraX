"""
Encapsulate the lifecycle function to automate the management of the app's lifecycle.
Read the app's lifetime in the configuration,
wait asynchronously until the dead time is reached, 
and then send a request to the node to release the shutdown signal.
Simultaneously initialize other independent services.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio, typing, types
from dataclasses import dataclass
import register, shutdown, cfg_monitor, restart_min_service
from src.cerebrax.tools.config import ConfigLoader, ConfigParser
from src.cerebrax.proxy.proxy_handler import ProxyHandler
from src.cerebrax.proxy.certificate_installer import CertificateInstaller


DefaultCfgDir = "/home/ckr-rpi/Desktop/CerebraX/src/cerebrax/tools"
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


async def load_cfg(path: str) -> ConfigParser:
    cfg = await ConfigLoader(path=path).async_load()  # 初始化加载配置文件
    cfg_parser = ConfigParser(cfg).parse()  # 构造config parser并解析文件
    return cfg_parser

async def reload_cfg(
        shared_instance: SharedInstances,
        event_flow: typing.AsyncGenerator
) -> None:
    async for path in event_flow:
        new_cfg_parser = await load_cfg(path=path)
        restarter = restart_min_service.RestartMinService(
            host="http://localhost:8000",
            base_cfg_parser=shared_instance.cfg_parser,
            new_cfg_parser=new_cfg_parser,
        )
        await restarter.restart()
        shared_instance.cfg_parser = new_cfg_parser
    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncGenerator:
    app.state = types.SimpleNamespace()  # 类型提示
    cfg_parser = await load_cfg(path=TomlPath)  # 加载配置文件
    shutdown_task = asyncio.create_task(  # 创建定时关闭服务任务
        shutdown.countdown(
            server=register.server,  # server 对象
            life_cycle=cfg_parser.lifespan_cfg.life_cycle,  # 服务的生命周期
            wait_for_exit=cfg_parser.lifespan_cfg.wait_for_exit,  # 等待退出的时间
        )
    )
    app.state.shared_instances = SharedInstances(
        cfg_parser=cfg_parser,  # 加载解析配置文件
        shutdown_task=shutdown_task,  # 将shutdown task注册到全局对象，用于取消定时关机
        server=register.server,  # 注册server实例
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
    config_monitor = cfg_monitor.ConfigFileEventMonitor(
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





