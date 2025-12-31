from src.cerebrax.common_depend import (
    typing,
)
from src.cerebrax.utils.collector import (
    DataCollector,
)


TIME = typing.Union[int, float]
DefaultLifeCycle: TIME = 0
DefaultWaitForExit: TIME = 0
DefaultExitTimeout: TIME = 10


DefaultStartupCommand: typing.List[str] = ["mitmdump"]
AutoStart: bool = False
AdaptPattern: bool = False
FallbackPattern: str = "mitmdump"
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}

DockerImageList = typing.Union[typing.List, typing.Dict]
DefaultContainerQuery: str = "CerebraX-OCR"
ContainerRunArgs = typing.Optional[typing.Dict[str, typing.Any]]

ResourceTypes: typing.Set[str] = {"network", "memory", "swap", "cpu", "disk"}
_data_collector = DataCollector()
ResourceMapping: typing.Dict[str, typing.Callable] = {
    "network": _data_collector.get_network_snapshot,
    "memory": _data_collector.get_memory_snapshot,
    "swap": _data_collector.get_swap_snapshot,
    "cpu": _data_collector.get_cpu_snapshot,
    "disk": _data_collector.get_disk_snapshot,
}
Interval = typing.Optional[float]

CommonIterable = typing.Union[
    typing.List,
    typing.Set,
    typing.Tuple
]


Platforms = typing.Literal["windows", "linux", "ios", "android", "firefox", "other-platform", "macos"]
OtherPlatformFormat = typing.Literal["pem", "p12"]
