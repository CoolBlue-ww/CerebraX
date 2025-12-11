import subprocess, os, typing, signal, asyncio


class ProxyHandler(object):
    def __init__(self, startup_command: typing.List[str]) -> None:
        self._startup_command = startup_command
        self._popen = None

    @property
    def popen(self) -> typing.Optional[subprocess.Popen]:
        return self._popen

    @popen.setter
    def popen(self, value: typing.Optional[subprocess.Popen]) -> None:
        self._popen = value

    def start(self) -> None:
        if not self.popen:
            self.popen = subprocess.Popen(self._startup_command)
        return None

    def stop(self) -> None:
        if self.popen and not self.popen.poll():
            os.kill(self.popen.pid, signal.SIGTERM)
            self.popen = None
        return None

__all__ = [
    "ProxyHandler"
]
