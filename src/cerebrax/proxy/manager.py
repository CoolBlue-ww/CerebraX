from threading import Thread
from mitmproxy.tools.dump import DumpMaster as MitmproxyMaster
from mitmproxy.options import Options as MitmproxyOptions
from mitmproxy.exceptions import AddonManagerError
import asyncio, logging, sys


logging.basicConfig(
    level=logging.DEBUG,  # 所有级别都打印
    format='%(message)s',  # 只输出裸消息，不带时间/模块名
    handlers=[logging.StreamHandler(sys.stdout)]  # 强制走到 stdout，print 同流
)
# 在创建子线程之前
import logging
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('mitmproxy').setLevel(logging.WARNING)


class Options(MitmproxyOptions):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(
            listen_host=host,
            listen_port=port,
        )


class Master(MitmproxyMaster):
    def __init__(self, options: Options, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(
            options=options,
            loop=loop,
            with_dumper=False,
            with_termlog=False,
        )


class ProxyManager(Thread):
    __slots__ = (
        '_host',
        '_port',
        '_options',
        '_master',
        '_loop',
        '_running',
        '_task',
    )
    useless_tasks = {
        'ClientPlayback.playback',
        'ProxyLauncher.launch',
        'Event.wait',
        'ConnectionHandler.wakeup',
        'ConnectionHandler.open_connection',
        'ServerInstance.handle_stream',
        'TimeoutWatchdog.watch',
        'ConnectionHandler.handle_connection',
    }
    useful_tasks = {
        'RequestResponseCycle.run_asgi',
        'Server.serve',
        'LifespanOn.main',
    }

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 8080
                 ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._loop = None
        self._options = None
        self._master = None

    @property
    def options(self) -> Options | None:
        return self._options

    @options.setter
    def options(self, value: Options) -> None:
        self._options = value

    @property
    def master(self) -> Master | None:
        return self._master

    @master.setter
    def master(self, value: Master) -> None:
        self._master = value

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        return self._loop

    @loop.setter
    def loop(self, value: asyncio.AbstractEventLoop | None) -> None:
        self._loop = value

    def launch(self) -> None:
        return super().start()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.core()
        return None

    def core(self) -> None:
        options = Options(host=self._host, port=self._port)
        master = Master(options=options, loop=self.loop)
        self.master = master
        self.options = options
        try:
            self.loop.run_until_complete(master.run())
        except (asyncio.CancelledError, RuntimeError):
            pass
        finally:
            self._uninstall_addons()
        return None

    def land(self) -> None:
        self.master.shutdown()
        if self.loop and not self.loop.is_closed():
            self._close_loop()
        self.join()
        return None

    def _close_loop(self) -> None:
        asyncio.run_coroutine_threadsafe(self._cleanup(), self.loop)
        self.loop.call_soon_threadsafe(self.loop.stop)
        try:
            self.loop.close()
            return None
        except RuntimeError:
            self._close_loop()
        return None

    def _uninstall_addons(self) -> None:
        for addon in self.master.addons.chain:
            try:
                self.master.addons.remove(addon=addon)
            except AddonManagerError:
                pass
        return None

    async def _cleanup(self) -> None:
        tasks = self._get_tasks()
        for t in tasks:
            t.cancel()
        await  asyncio.gather(*tasks, return_exceptions=True)
        return None

    def _get_tasks(self) -> list[asyncio.Task]:
        tasks = [t for t in asyncio.all_tasks(self.loop)
                 if t is not asyncio.current_task()]
        return tasks


__all__ = [
    'ProxyManager',
]
