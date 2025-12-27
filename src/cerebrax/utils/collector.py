from src.cerebrax.common_depend import (
    typing,
    psutil,
)

class DataCollector(object):
    @staticmethod
    def get_memory_snapshot():
        memory_snapshot = psutil.virtual_memory()
        return memory_snapshot

    @staticmethod
    def get_swap_snapshot():
        swap_snapshot = psutil.swap_memory()
        return swap_snapshot

    @staticmethod
    def get_cpu_snapshot(interval: typing.Optional[float] = None):
        cpu_snapshot = {
            'cpu_count': {
                'logical': psutil.cpu_count(logical=True),
                'physical': psutil.cpu_count(logical=False),
            },
            'cpu_percent': {
                'average': psutil.cpu_percent(interval=interval, percpu=False),
                'respective': psutil.cpu_percent(interval=interval, percpu=True),
            },
            'cpu_times': {
                'average': psutil.cpu_times(percpu=False),
                'respective': psutil.cpu_times(percpu=True),
            },
            'cpu_stats': psutil.cpu_stats(),
            'getloadavg': psutil.getloadavg(),
        }
        return cpu_snapshot

    @staticmethod
    def get_network_snapshot():
        network_snapshot = {
            'network_io': {
                'average': psutil.net_io_counters(pernic=False),
                'respective': psutil.net_io_counters(pernic=True),
            }
        }
        return network_snapshot

    @staticmethod
    def get_disk_snapshot():
        disk_partitions = psutil.disk_partitions()
        disk_usage = {i.mountpoint: psutil.disk_usage(i.mountpoint) for i in disk_partitions}
        disk_snapshot = {
            'disk_usage': disk_usage,
            'disk_partitions': disk_partitions,
            'disk_io': {
                'average': psutil.disk_io_counters(perdisk=False, nowrap=True),
                'respective': psutil.disk_io_counters(perdisk=True, nowrap=True),
            },
        }
        return disk_snapshot

__all__ = [
    "DataCollector",
]
