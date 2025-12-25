from server import ServerHandler
from app import app
import register
import asyncio, typing
from uvicorn import Server

DEFAULT_ARGS = {
    'app': app,
    'host': '127.0.0.1',
    'port': 8000,
}

class Myfsp(object):
    def __init__(self, args: typing.Dict[str, typing.Any] = None) -> None:
        self._args = args if isinstance(args, typing.Dict) else DEFAULT_ARGS
        self._server = ServerHandler(
            args=self._args,
        ).build_server()
        register.server = self._server  # injection
        register.server_args = self._args

    @property
    def server(self) -> Server:
        return self._server

    def run(self) -> None:
        asyncio.run(self.server.serve())
        return None

atc = Myfsp()
atc.run()

