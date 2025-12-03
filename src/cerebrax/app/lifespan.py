"""
Encapsulate the lifecycle function to automate the management of the app's lifecycle.
Read the app's lifetime in the configuration,
wait asynchronously until the dead time is reached, 
and then send a request to the node to release the shutdown signal.
Simultaneously initialize other independent services.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio, typing, types, aiopath

from watchdog.utils import load_module

import _register
from uvicorn import Server
from pydantic import BaseModel
from config.config import Config
from database.memory_database import RedisHandler
from request.client import PlaywrightClient, HttpxClient
from monitor.monitor import Addon, Addons, Options, SystemMonitor, ConfigFileEventMonitor
from proxy.certificate import MitmproxyCertificate
from proxy.loader import Loader, AddonInstanceCreator
from proxy.manager import ProxyManager


async def async_set_exit(wait: typing.Union[int, float], server: typing.Optional[Server]) -> None:
    if wait > 0:
        await asyncio.sleep(wait)
    server.should_exit = True
    return None

async def app_lifespan(server: Server, life_cycle: _register.TIME = 10, wait: _register.TIME = 0) -> typing.Optional[str]:
    if life_cycle > 0:
        await asyncio.sleep(life_cycle)
        await async_set_exit(wait=wait, server=server)
    return None

class LifespanConfig(BaseModel):
    life_cycle: _register.TIME = _register.DefaultLifeCycle
    wait: _register.TIME = _register.DefaultWait
    timeout: _register.TIME = _register.DefaultTimeout

def parse_lifespan_cfg(cfg: typing.Dict) -> LifespanConfig:
    lifespan_cfg = cfg.pop("Lifespan", {})
    return LifespanConfig(**lifespan_cfg)

class RedisConfig(BaseModel):
    auto_connection: bool = False
    redis_id: typing.Union[str, None] = None
    redis_options: typing.Dict[str, typing.Any] = {}

class SQLiteConfig(BaseModel):
    a: str = None
    b: str = None

def parser_database_cfg(cfg: typing.Dict) -> typing.Tuple[RedisConfig, SQLiteConfig]:
    database_cfg = cfg.pop("Database", {})
    return RedisConfig(**database_cfg["Redis"]), SQLiteConfig(**database_cfg["SQLite"])

async def parser_monitor_cfg(cfg: typing.Dict) -> typing.Any:
    monitor_cfg = cfg.pop("Monitor", {})
    system_monitor_cfg_path, s_instance_name = monitor_cfg["system_monitor_options"].rsplit(":", maxsplit=1)
    config_file_event_monitor_path, c_instance_name = monitor_cfg["config_file_event_monitor_options"].rsplit(":", maxsplit=1)
    # 加载Python对象文件
    load_modules = [
        Loader(load_path=system_monitor_cfg_path).async_load_module(),
        Loader(load_path=config_file_event_monitor_path).async_load_module(),
    ]
    s_module, c_module = await asyncio.gather(*load_modules, return_exceptions=True)
    return getattr(s_module, s_instance_name), getattr(c_module, c_instance_name)


DefaultCfgDir = "/home/ckr-ubuntu/桌面/myfsp/myfsp/config/"
TomlPath = DefaultCfgDir + "settings.toml"
PyPath = DefaultCfgDir + "settings.py"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = types.SimpleNamespace()  # 类型提示
    app.state.server = _register.server  # 传递server对象
    cfg = await Config(path=TomlPath).async_load()  # 加载配置文件
    lifespan_cfg = parse_lifespan_cfg(cfg=cfg)  # 解析生命周相关参数
    redis_cfg, sqlite_cfg = parser_database_cfg(cfg=cfg)  # Redis，SQLite数据库初始化参数
    system_monitor_cfg, config_file_event_monitor_cfg = await parser_monitor_cfg(cfg=cfg)  # 解析Monitor参数
    app.state.redis_handler = RedisHandler(  # 初始化Redis Handler
        auto_connection=redis_cfg.auto_connection,
        redis_id=redis_cfg.redis_id,
        redis_options=redis_cfg.redis_options,
    )
    system_monitor = SystemMonitor(options=system_monitor_cfg)  # 构建SystemMonitor对象
    await system_monitor.start()  # 开启系统资源监控
    shutdown_task = asyncio.create_task(  # 创建定时关闭服务任务
        app_lifespan(
            server=_register.server,
            life_cycle=lifespan_cfg.life_cycle,
            wait=lifespan_cfg.wait,
        )
    )
    # -------------------------------------------------------------
    yield
    # -------------------------------------------------------------

    try:
        await asyncio.wait_for(shutdown_task, timeout=lifespan_cfg.timeout)
    except asyncio.TimeoutError:
        pass  # 未到达设置时长手动退出







