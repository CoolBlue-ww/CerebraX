import subprocess, os, typing, signal


class ProxyHandler(object):
    def __init__(self, args: typing.List[str]) -> None:
        self._args = args
        self._pid = None
        self._running = False

    @property
    def pid(self) -> typing.Optional[int]:
        return self._pid

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if not self._running:
            result = subprocess.Popen(self._args)
            self._pid = result.pid
            self._running = True
        return None

    def stop(self) -> None:
        if self._pid:
            os.kill(self.pid, signal.SIGTERM)
            self._pid = None
            self._running = False
        return None

__all__ = [
    "ProxyHandler"
]

