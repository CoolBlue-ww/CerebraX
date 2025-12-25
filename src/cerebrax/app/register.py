from server import SubServer
import typing

"""
Register global variables in the registry
"""
server: typing.Optional[SubServer] = None  # server
server_args: typing.Optional[typing.Dict[str, typing.Any]] = None  # server_args

__all__ = [
    "server",
    "server_args",
]
