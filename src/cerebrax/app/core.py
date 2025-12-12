from server import ServerHandler
from app import app
import register
import asyncio, platform, os, signal
from uvicorn import Server


class Myfsp(object):
    def __init__(self):
        self._server = ServerHandler(args={
                'app': app,
                'host': '127.0.0.1',
                'port': 8000,
            }).build_server()
        register.server = self._server  # injection

    @property
    def server(self) -> Server:
        return self._server

    def run(self) -> None:
        asyncio.run(self.server.serve())
        return None

atc = Myfsp()
atc.run()

