from server import SubServer
import typing

"""
Register global variables in the registry
"""
server: typing.Optional[SubServer] = None  # server


__all__ = [
    "server",
]
