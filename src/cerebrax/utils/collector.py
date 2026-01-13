from src.cerebrax.common_depend import (
    typing,
    psutil,
    ThreadPoolExecutor,
)
from src.cerebrax.internal import (thread_pool)

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
    def get_cpu_snapshot(executor: ThreadPoolExecutor, interval: typing.Optional[float] = None):
        cpu_percent_average_future = executor.submit(psutil.cpu_percent, interval=interval, percpu=False)
        cpu_percent_respective_future = executor.submit(psutil.cpu_percent, interval=interval, percpu=True)
        cpu_snapshot = {
            'cpu_count': {
                'logical': psutil.cpu_count(logical=True),
                'physical': psutil.cpu_count(logical=False),
            },
            'cpu_percent': {
                "average": cpu_percent_average_future.result(),
                'respective': cpu_percent_respective_future.result(),
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
        disk_partitions_physical = psutil.disk_partitions(all=False)
        # disk_partitions_all = psutil.disk_partitions(all=True)
        disk_usage_physical = {i.mountpoint: psutil.disk_usage(i.mountpoint) for i in disk_partitions_physical}

        # disk_usage_all = {}
        # for i in disk_partitions_all:
        #     try:
        #         disk_usage_all[i.mountpoint] = psutil.disk_usage(i.mountpoint)
        #     except PermissionError as e:
        #         disk_usage_all[i.mountpoint] = e
        disk_snapshot = {
            'disk_usage': {
                "physical": disk_usage_physical,
                # "all": disk_usage_all,
            },
            'disk_partitions': {
                "physical": disk_partitions_physical,
                # "all": disk_partitions_all,
            },
            'disk_io': {
                'average': psutil.disk_io_counters(perdisk=False, nowrap=True),
                'respective': psutil.disk_io_counters(perdisk=True, nowrap=True),
            },
        }
        return disk_snapshot

__all__ = [
    "DataCollector",
]


# import time
# d = DataCollector()
# a = time.time()
# count = 0
# while count <= 100000:
#     d.get_memory_snapshot()
#     d.get_swap_snapshot()
#     d.get_cpu_snapshot(thread_pool)
#     d.get_network_snapshot()
#     d.get_disk_snapshot()
#     count += 1
#     time.sleep(0.001)
# b = time.time()
# print(f"总共采样次数：{count-1}，平均单次的采样时间为：{((b-a)/count)*1000}ms")