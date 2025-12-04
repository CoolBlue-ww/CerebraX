import typing, sys, shlex
from pydantic import (
    BaseModel,
    field_validator,
    ValidationInfo,
    ValidationError
)


TIME = typing.Union[int, float]
DefaultLifeCycle: TIME = 0
DefaultWaitForExit: TIME = 1
DefaultExitTimeout: TIME = 1

class LifespanConfig(BaseModel):
    life_cycle: TIME = DefaultLifeCycle
    wait_for_exit: TIME = DefaultWaitForExit
    exit_timeout: TIME = DefaultExitTimeout

DefaultCommand: typing.List[str] = ["mitmdump"]
AdaptPattern: bool = False
FallbackPattern: str = "mitmdump"
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}

class ProxyConfig(BaseModel):
    adapt_pattern: bool = AdaptPattern
    fallback_pattern: str = FallbackPattern
    command: typing.Union[str, typing.List[str]] = DefaultCommand


    @field_validator("command", mode="before")
    @classmethod
    def correct_pattern(cls, v: typing.Union[str, typing.List[str]], info: ValidationInfo) -> typing.List[str]:
        if isinstance(v, str):
            v = shlex.split(v)
        if v[0] not in Patterns:
            raise ValidationError(f"{v[0]} is not a valid pattern")
        _data = info.data
        if v[0] == "mitmproxy":
            if not sys.stdin.isatty() and _data["adapt_pattern"]:
                fallback_pattern = _data["fallback_pattern"]
                if fallback_pattern != "mitmproxy" and fallback_pattern in Patterns:
                    v[0] = fallback_pattern
                else:
                    v[0] = "mitmdump"
        return v


class ShutdownJsonItem(BaseModel):
    wait_for_exit: TIME = DefaultWaitForExit

