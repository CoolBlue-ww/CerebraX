from src.cerebrax.common_depend import (
    typing,
)
from src.cerebrax.utils import collector


Time = typing.Union[int, float]
DefaultLifeCycle: Time = 0
DefaultWaitForExit: Time = 0

DefaultStartupCommand: typing.List[str] = ["mitmdump"]
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}

DockerImageList = typing.Union[typing.List, typing.Dict]
DefaultContainerQuery: str = "CerebraX-OCR"
ContainerRunArgs = typing.Optional[typing.Dict[str, typing.Any]]


ResourceTypes: typing.Set[str] = {"network", "memory", "swap", "cpu", "disk"}
CPU_COUNT = collector.cpu_count
CollectionMethods: typing.Dict[str, typing.Callable] = {
    "network": collector.get_network_snapshot,
    "memory": collector.get_memory_snapshot,
    "swap": collector.get_swap_snapshot,
    "cpu": collector.get_cpu_snapshot,
    "disk": collector.get_disk_snapshot,
}
Interval = typing.Optional[float]

CommonIterable = typing.Union[
    typing.List,
    typing.Set,
    typing.Tuple
]

Platforms = typing.Literal["windows", "linux", "ios", "android", "firefox", "other-platform", "macos"]
OtherPlatformFormat = typing.Literal["pem", "p12"]
