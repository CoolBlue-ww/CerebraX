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
import register, shutdown
from src.cerebrax.tools.config import ConfigLoader, ConfigParser
from src.cerebrax.proxy.proxy_handler import ProxyHandler


DefaultCfgDir = "/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/tools/"
TomlPath = DefaultCfgDir + "settings.toml"
PyPath = DefaultCfgDir + "settings.py"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = types.SimpleNamespace()  # 类型提示
    app.state.server = register.server  # 传递server对象
    cfg_loader = await ConfigLoader(path=TomlPath).async_load()  # 初始化加载配置文件
    cfg_parser = ConfigParser(cfg_loader).parse()  # 解析配置文件
    proxy_handler = ProxyHandler(args=cfg_parser.proxy_cfg.command)  # 初始化Proxy Handler对象
    proxy_handler.start()  # 开启代理
    app.state.proxy_handler = proxy_handler  # 全局注册
    shutdown_task = asyncio.create_task(  # 创建定时关闭服务任务
        shutdown.countdown(
            server=register.server,
            life_cycle=cfg_parser.lifespan_cfg.life_cycle,
            wait_for_exit=cfg_parser.lifespan_cfg.wait_for_exit,
        )
    )
    # -------------------------------------------------------------
    yield
    # -------------------------------------------------------------

    try:
        await asyncio.wait_for(shutdown_task, timeout=cfg_parser.lifespan_cfg.exit_timeout)
    except asyncio.TimeoutError:
        pass  # 未到达设置时长手动退出







