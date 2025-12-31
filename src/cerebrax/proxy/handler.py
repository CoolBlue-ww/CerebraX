from src.cerebrax.common_depend import (
    typing,
    asyncio,
    subprocess,
    os,
    signal,
)

class ProxyHandler(object):
    def __init__(self, startup_command: typing.List[str]) -> None:
        self._startup_command = startup_command
        self.popen = None
        self.running = False
        self._check_task = None

    async def check_alive(self) -> None:
        while True:
            return_code = self.popen.poll()
            if return_code:
                self.running = False
                self.popen = None
                break
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    def start(self) -> None:
        if not self.popen:
            self.running = True
            self.popen = subprocess.Popen(self._startup_command)
            self._check_task = asyncio.create_task(self.check_alive())

    async def stop(self) -> None:
        if self.popen and self.running:
            os.kill(self.popen.pid, signal.SIGTERM)
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self.popen = None
            self.running = False
            self._check_task = None
        if self._check_task:
            await self._check_task
            self._check_task = None


__all__ = [
    "ProxyHandler"
]
