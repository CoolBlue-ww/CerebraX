from server import SubServer
import typing

"""
Register global variables in the registry
"""
server: typing.Optional[SubServer] = None  # server

TIME = typing.Union[int, float]

DefaultTimeout = 1

DefaultLifeCycle = 0

DefaultWait = 1
