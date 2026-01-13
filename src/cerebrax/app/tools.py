from src.cerebrax.common_depend import (
    time,
    asyncio,
)
from src.cerebrax._types import (
    Time,
)
import src.cerebrax.app.register


# http请求关机的同步方法
def sync_set_exit(wait_for_exit: Time, server: src.cerebrax.app.register.SubServer) -> None:
    if wait_for_exit > 0:
        time.sleep(wait_for_exit)
    server.should_exit = True
    return None

# 自动关闭服务的异步方法
async def async_set_exit(wait_for_exit: Time, server: src.cerebrax.app.register.SubServer) -> None:
    if wait_for_exit > 0:
        await asyncio.sleep(wait_for_exit)
    server.should_exit = True
    return None

# 关机计时器，指有当life_cycle参数大于0的时候才生效
async def countdown(server: src.cerebrax.app.register.SubServer, life_cycle: Time, wait_for_exit: Time) -> None:
    if life_cycle > 0:
        try:
            await asyncio.sleep(life_cycle)
        except asyncio.CancelledError:
            return None
        else:
            await async_set_exit(wait_for_exit=wait_for_exit, server=server)
    return None

