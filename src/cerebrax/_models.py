from src.cerebrax.common_depend import (
sys,
shlex,
typing,
BaseModel,
field_validator,
ValidationError,
ValidationInfo
)
from src.cerebrax._types import (
    Time,
    DefaultLifeCycle,
    DefaultStartupCommand,
    DefaultWaitForExit,
    Patterns,
)


class LifespanConfig(BaseModel):
    life_cycle: Time = DefaultLifeCycle
    wait_for_exit: Time = DefaultWaitForExit


class ProxyConfig(BaseModel):
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
                _v[0] = "mitmdump"
        return _v


class ShutdownConfirm(BaseModel):
    shutdown: bool = True
    wait_for_exit: Time = DefaultWaitForExit

class CannelCountdown(BaseModel):
    cannel_countdown: bool = False

