from src.cerebrax.common_depend import typing

TIME = typing.Union[int, float]
DefaultLifeCycle: TIME = 0
DefaultWaitForExit: TIME = 0
DefaultExitTimeout: TIME = 10



DefaultStartupCommand: typing.List[str] = ["mitmdump"]
AutoStart: bool = False
AdaptPattern: bool = False
FallbackPattern: str = "mitmdump"
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}