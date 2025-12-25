import typing, sys, shlex
from pydantic import (
    BaseModel,
    field_validator,
    ValidationInfo,
    ValidationError
)

TIME = typing.Union[int, float]
DefaultLifeCycle: TIME = 0
DefaultWaitForExit: TIME = 0
DefaultExitTimeout: TIME = 10

class LifespanConfig(BaseModel):
    life_cycle: TIME = DefaultLifeCycle
    wait_for_exit: TIME = DefaultWaitForExit
    exit_timeout: TIME = DefaultExitTimeout


DefaultStartupCommand: typing.List[str] = ["mitmdump"]
AutoStart: bool = False
AdaptPattern: bool = False
FallbackPattern: str = "mitmdump"
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}


class ProxyConfig(BaseModel):
    auto_start: bool = AutoStart
    adapt_pattern: bool = AdaptPattern
    fallback_pattern: str = FallbackPattern
    startup_command: typing.Union[str, typing.List[str]] = DefaultStartupCommand

    @field_validator("startup_command", mode="before")
    @classmethod
    def correct_pattern(cls, v: typing.Union[str, typing.List[str]], info: ValidationInfo) -> typing.List[str]:
        _v = v
        if isinstance(v, str):
            _v = shlex.split(v)
        if _v[0] not in Patterns:
            raise ValidationError(f"{_v[0]} is not a valid pattern")
        _data = info.data
        if _v[0] == "mitmproxy":
            if not sys.stdin.isatty() and _data["adapt_pattern"]:
                fallback_pattern = _data["fallback_pattern"]
                if fallback_pattern != "mitmproxy" and fallback_pattern in Patterns:
                    _v[0] = fallback_pattern
                else:
                    _v[0] = "mitmdump"
        return _v


class ShutdownLaunchItem(BaseModel):
    shutdown: bool = True
    wait_for_exit: TIME = DefaultWaitForExit


class CannelCountdownItem(BaseModel):
    cannel_countdown: bool = False
