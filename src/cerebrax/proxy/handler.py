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
        self._popen = None
        self._running = False
        self._is_running_task = None

    @property
    def is_running_task(self) -> typing.Optional[asyncio.Task]:
        return self._is_running_task

    @is_running_task.setter
    def is_running_task(self, value: typing.Optional[asyncio.Task]) -> None:
        self._is_running_task = value

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    @property
    def popen(self) -> typing.Optional[subprocess.Popen]:
        return self._popen

    @popen.setter
    def popen(self, value: typing.Optional[subprocess.Popen]) -> None:
        self._popen = value

    async def is_running(self) -> None:
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
        return None

    def start(self) -> None:
        if not self.popen:
            self.running = True
            self.popen = subprocess.Popen(self._startup_command)
            self.is_running_task = asyncio.create_task(self.is_running())
        return None

    async def stop(self) -> None:
        if self.popen and self.running:
            os.kill(self.popen.pid, signal.SIGTERM)
            self.is_running_task.cancel()
            try:
                await self.is_running_task
            except asyncio.CancelledError:
                pass
            self.popen = None
            self.running = False
            self.is_running_task = None
        if self.is_running_task:
            await self.is_running_task
            self.is_running_task = None
        return None

__all__ = [
    "ProxyHandler"
]
