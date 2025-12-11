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
import register, shutdown
from src.cerebrax.tools.config import ConfigLoader, ConfigParser
from src.cerebrax.proxy.proxy_handler import ProxyHandler


DefaultCfgDir = "/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/tools/"
TomlPath = DefaultCfgDir + "settings.toml"
PyPath = DefaultCfgDir + "settings.py"


"""
实现类依赖汇集容器
"""
@dataclass
class ImplementationClasses(object):
    config_loader: type[ConfigLoader]
    config_parser: type[ConfigParser]
    proxy_handler: type[ProxyHandler]

@dataclass
class SharedInstances(object):
    cfg_parser: typing.Optional[ConfigParser] = None
    proxy_handler: typing.Optional[ProxyHandler] = None
    shutdown_task: typing.Optional[asyncio.Task] = None
    server: typing.Optional[register.SubServer] = None

async def initial_loading_cfg(path: str) -> ConfigParser:
    cfg_loader = await ConfigLoader(path=path).async_load()  # 初始化加载配置文件
    cfg_parser = ConfigParser(cfg_loader).parse()  # 构造config parser并解析文件
    return cfg_parser

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = types.SimpleNamespace()  # 类型提示
    cfg_parser = await initial_loading_cfg(path=TomlPath)  # 加载配置文件
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
    app.state.implementation_class = ImplementationClasses(
        config_parser=ConfigParser, # 配置文件解析实现类
        config_loader=ConfigLoader,  # 配置文件加载实现类
        proxy_handler=ProxyHandler,  # 代理控制实现类
    )
    # -------------------------------------------------------------
    yield
    # -------------------------------------------------------------

    try:
        await asyncio.wait_for(
            fut=shutdown_task,  # 等待关机任务
            timeout=cfg_parser.lifespan_cfg.exit_timeout  # 等待超时时间
        )
    except asyncio.TimeoutError:
        pass  # 未到达设置时长手动退出





