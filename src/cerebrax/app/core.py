from server import ServerHandler
from app import app
import _register
import asyncio, platform, os, signal
from uvicorn import Server


class Myfsp(object):
    def __init__(self):
        self._server = ServerHandler(args={
                'app': app,
                'host': '127.0.0.1',
                'port': 8000,
            }).build_server()
        _register.server = self._server  # injection

    @property
    def server(self) -> Server:
        return self._server
    # async def _serve(self) -> None:
    #     try:
    #         await asyncio.wait_for(self.server.serve(), timeout=5)
    #     except asyncio.TimeoutError:
    #         system = platform.system()
    #         if system == 'Windows':
    #             pid, sig = os.getpid(), signal.CTRL_C_EVENT
    #             os.kill(pid, sig)
    #         if system in {'Linux', 'MacOS', 'Darwin'}:
    #             pid, sig = os.getpid(), signal.SIGTERM
    #             os.kill(pid, sig)
    #     return None

    def run(self) -> None:
        asyncio.run(self.server.serve())
        return None

atc = Myfsp()
atc.run()

