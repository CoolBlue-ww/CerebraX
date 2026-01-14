from src.cerebrax.common_depend import (
    dataclass,
    typing,
    namedtuple,
)


@dataclass(frozen=True)
class ConfigSnapshot(object):
    lifespan_config: typing.Any = None
    proxy_config: typing.Any = None


@dataclass(frozen=False)
class Shared(object):
    pass


@dataclass(frozen=False)
class Toolkit(object):
    pass

class MemorySnapshot(typing.NamedTuple):
    virtual_memory: typing.Any

class SwapSnapshot(typing.NamedTuple):
    swap_memory: typing.Any

class CPUCount(typing.NamedTuple):
    physical: int
    logical: int

class CPUSnapshot(typing.NamedTuple):
    cpu_percent: typing.Any
    cpu_times: typing.Any
    cpu_times_percent: typing.Any
    cpu_stats: typing.Any
    cpu_freq: typing.Any

class NetworkSnapshot(typing.NamedTuple):
    net_io_counters: typing.Any

class DiskSnapshot(typing.NamedTuple):
    disk_usages: typing.Any
    disk_partitions: typing.Any
    disk_io_counters: typing.Any


__all__ = [
    "ConfigSnapshot",
    "Shared",
    "Toolkit",
    "MemorySnapshot",
    "SwapSnapshot",
    "CPUCount",
    "CPUSnapshot",
    "NetworkSnapshot",
    "DiskSnapshot",
]
