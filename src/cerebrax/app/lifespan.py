"""
Encapsulate the lifecycle function to automate the management of the app's lifecycle.
Read the app's lifetime in the configuration,
wait asynchronously until the dead time is reached, 
and then send a request to the node to release the shutdown signal.
Simultaneously initialize other independent services.
"""

from src.cerebrax.common_depend import (
    typing, asyncio,
    asynccontextmanager,
    FastAPI,
)
import register, tools


DefaultCfgDir = "/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/utils"
TomlPath = DefaultCfgDir + "/settings.toml"
PyPath = DefaultCfgDir + "settings.py"


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncGenerator:
    shutdown_task = asyncio.create_task(  # 创建定时关闭服务任务
        tools.countdown(
            server=register.server,  # server 对象
            life_cycle=cfg_parser.lifespan_cfg.life_cycle,  # 服务的生命周期
            wait_for_exit=cfg_parser.lifespan_cfg.wait_for_exit,  # 等待退出的时间
        )
    )
    # -------------------------------------------------------------
    yield
    # -------------------------------------------------------------
    try:
        await asyncio.wait_for(
            fut=shutdown_task,  # 等待关机任务
            timeout=0  # 立马返回
        )
    except asyncio.TimeoutError:
        pass  # 未到达设置时长手动退出





