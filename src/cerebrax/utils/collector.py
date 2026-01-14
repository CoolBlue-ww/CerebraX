from src.cerebrax.common_depend import (
    psutil,
)
from src.cerebrax._container import (
    MemorySnapshot,
    SwapSnapshot,
    CPUCount,
    CPUSnapshot,
    NetworkSnapshot,
    DiskSnapshot,
)


def get_memory_snapshot() -> MemorySnapshot:
    memory_snapshot = MemorySnapshot(
        psutil.virtual_memory()
    )
    return memory_snapshot


def get_swap_snapshot() -> SwapSnapshot:
    swap_snapshot = SwapSnapshot(
        psutil.swap_memory()
    )
    return swap_snapshot


cpu_count = CPUCount(
    psutil.cpu_count(logical=False),
    psutil.cpu_count(logical=True)
)


def get_cpu_snapshot() -> CPUSnapshot:
    cpu_snapshot = CPUSnapshot(
        psutil.cpu_percent(interval=None, percpu=False),
        psutil.cpu_times(percpu=False),
        psutil.cpu_times_percent(percpu=False),
        psutil.cpu_stats(),
        psutil.cpu_freq(percpu=False)
    )
    return cpu_snapshot


def get_network_snapshot() -> NetworkSnapshot:
    network_snapshot = NetworkSnapshot(
        psutil.net_io_counters(pernic=False, nowrap=True)
    )
    return network_snapshot


def get_disk_snapshot() -> DiskSnapshot:
    disk_partitions = psutil.disk_partitions(all=False)
    paths = [m.mountpoint for m in disk_partitions]
    disk_usages = {p: psutil.disk_usage(p) for p in paths}
    disk_snapshot = DiskSnapshot(
        disk_usages,
        disk_partitions,
        psutil.disk_io_counters(perdisk=False, nowrap=True),
    )
    return disk_snapshot


__all__ = [
    "get_memory_snapshot",
    "get_swap_snapshot",
    "get_cpu_snapshot",
    "get_network_snapshot",
    "get_disk_snapshot",
    "cpu_count",
]
