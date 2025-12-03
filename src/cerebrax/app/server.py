from uvicorn import Server, Config
from typing import Dict, Any, Optional, List


class SubServer(Server):
    def __init__(self, config: Config) -> None:
        super().__init__(config=config)
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        if isinstance(value, bool):
            self._running = value

    async def serve(self, sockets: Optional[List] = None) -> None:
        self.running = True
        try:
            await super().serve(sockets=sockets)
        finally:
            self.running = False
        return None

class ServerHandler(object):
    __slots__ = ("_args", )

    def __init__(self, args: Dict[str, Any])-> None:
        self._args = args

    def build_server(self) -> Server:
        config = Config(
            **self._args
        )
        server = SubServer(config=config)
        return server


__all__ = [
    'SubServer',
    'ServerHandler',
]

