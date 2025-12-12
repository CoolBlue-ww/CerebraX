import asyncio, inspect, psutil, typing
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent
from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationInfo, ValidationError

"""
包装存放获取到的系统状态参数的容器类 start
"""
@dataclass
class Memory(object):
    memory_snapshot: typing.Any

@dataclass
class Swap(object):
    swap_snapshot: typing.Any

@dataclass
class CPU(object):
    cpu_snapshot: typing.Any

@dataclass
class Disk(object):
    disk_snapshot: typing.Any

@dataclass
class Network(object):
    network_snapshot: typing.Any
"""
包装存放获取到的系统状态参数的容器类 end
"""

"""
获取系统状态数据的采集者类 start
"""
class DataCollector(object):
    @staticmethod
    def get_memory_snapshot() -> Memory:
        return Memory(memory_snapshot=psutil.virtual_memory())

    @staticmethod
    def get_swap_snapshot() -> Swap:
        return Swap(swap_snapshot=psutil.swap_memory())

    @staticmethod
    def get_cpu_snapshot(interval: float | None = None) -> CPU:
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
        return CPU(cpu_snapshot=cpu_snapshot)

    @staticmethod
    def get_network_snapshot() -> Network:
        network_snapshot = {
            'network_io': {
                'average': psutil.net_io_counters(pernic=False),
                'respective': psutil.net_io_counters(pernic=True),
            }
        }
        return Network(network_snapshot=network_snapshot)

    @staticmethod
    def get_disk_snapshot() -> Disk:
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
        return Disk(disk_snapshot=disk_snapshot)
"""
获取系统状态数据的采集者类 end
"""

"""
可复用线程池 start
"""
class ReusableThreadPool(object):
    def __init__(self) -> None:
        self.executor = None

    def start(self, max_workers: int | None = None) -> None:
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        return None

    def stop(self) -> None:
        if self.executor is not None:
            self.executor.shutdown()
            self.executor = None
        return None

    def map(self, func: typing.Callable, args: typing.Iterable, timeout: float | None = None,chunk_size: int = 1) -> typing.Generator:
        if not self.executor:
            empty_gen = (x for x in ())
            return empty_gen
        result = getattr(self.executor, 'map')(func, *args, timeout=timeout, chunk_size=chunk_size)
        return result

    def submit(self, func: typing.Callable, *args, **kwargs) -> typing.Any:
        if not self.executor:
            return None
        result = getattr(self.executor, 'submit')(func, *args, **kwargs).result()
        return result

    def submits(self, tasks: typing.Iterable[tuple[typing.Any, ...]], ordered: bool = False) -> list[typing.Any]:
        if not self.executor:
            return []
        submit_futures = []
        for task in tasks:
            func, args = task[0], task[1:]
            if not isinstance(func, typing.Callable):
                raise RuntimeError('Task must be callable')
            submit_futures.append(
                getattr(self.executor, 'submit')(func, *args)
            )
        iterator = as_completed(submit_futures) if not ordered else submit_futures
        results = [obj.result() for obj in iterator]
        return results
"""
可复用线程池 end
"""

"""
插件校验模型类 start
"""
def _has_explicit_param(func, name: str = "item") -> bool:
    return name in inspect.signature(func).parameters

def _is_coroutine_function(obj: typing.Any) -> bool:
    return inspect.iscoroutinefunction(obj)

def _anticipant_callable(func: typing.Callable) -> bool:
    if _has_explicit_param(func) and _is_coroutine_function(func):
        return True
    else:
        return False

class Addon(BaseModel):
    unite: typing.Callable
    test: int = 1

    @field_validator("unite", mode="before")
    @classmethod
    def _check_unite(cls, v: typing.Callable) -> typing.Callable:
        if not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

# async def p(item): pass
# a = Addon(unite=p)
# print(a)

class Addons(BaseModel):
    memory: typing.Optional[typing.Callable] = None
    swap: typing.Optional[typing.Callable] = None
    cpu: typing.Optional[typing.Callable] = None
    disk: typing.Optional[typing.Callable] = None
    network: typing.Optional[typing.Callable] = None

    @field_validator("memory", mode="before")
    @classmethod
    def _check_memory(cls, v: typing.Optional[typing.Callable]) -> typing.Optional[typing.Callable]:
        if v is not None and not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

    @field_validator("swap", mode="before")
    @classmethod
    def _check_swap(cls, v: typing.Optional[typing.Callable]) -> typing.Optional[typing.Callable]:
        if v is not None and not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

    @field_validator("cpu", mode="before")
    @classmethod
    def _check_cpu(cls, v: typing.Optional[typing.Callable]) -> typing.Optional[typing.Callable]:
        if v is not None and not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

    @field_validator("disk", mode="before")
    @classmethod
    def _check_disk(cls, v: typing.Optional[typing.Callable]) -> typing.Optional[typing.Callable]:
        if v is not None and not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

    @field_validator("network", mode="before")
    @classmethod
    def _check_network(cls, v: typing.Optional[typing.Callable]) -> typing.Optional[typing.Callable]:
        if v is not None and not _anticipant_callable(v):
            raise ValidationError(f"{v}不是期望的Callable")
        return v

"""
插件校验模型类 end
"""

"""
监控者的配置类 start
"""
Monitoring = {'memory', 'swap', 'cpu', 'disk', 'network'}

class Options(BaseModel):
    monitoring: typing.Union[list, set, tuple] = ('memory', 'swap', 'cpu', 'disk', 'network')
    unite_async_generator: bool = True
    addons: typing.Union[Addon, Addons]
    refresh_interval: typing.Union[int, float] = 1
    thread_pool_max_workers: int = 10
    channel_queue_max_size: int = 0

    @field_validator("refresh_interval", mode="before")
    @classmethod
    def _check_refresh_interval(cls, v: typing.Union[int, float]) -> typing.Union[int, float]:
        if v < 0:
            return 0
        else:
            return v

    @field_validator("thread_pool_max_workers", mode="before")
    @classmethod
    def _check_thread_pool_max_workers(cls, v: int) -> int:
        if v <= 0:
            return 1
        else:
            return v

    @field_validator("channel_queue_max_size", mode="before")
    @classmethod
    def _channel_queue_max_size(cls, v: int) -> int:
        if v < 0:
            return 0
        else:
            return v

    @field_validator("monitoring", mode="before")
    @classmethod
    def _check_monitoring(cls, v: typing.Union[list, set, tuple]) -> typing.Union[list, set, tuple]:
        if not v:
            raise ValidationError("监控选项不能为空。")
        for i in v:
            if i not in Monitoring:
                raise ValidationError(f"未知选项{i}")
        return v

    @field_validator("addons", mode="before")
    @classmethod
    def _check_addons(cls, v: typing.Union[Addon, Addons], info: ValidationInfo) -> typing.Union[Addon, Addons]:
        is_unite = info.data.get("unite_async_generator", True)
        monitoring = info.data.get("monitoring", Monitoring)
        if is_unite:
            if not isinstance(v, Addon):
                raise ValidationError("必须为Addon类型")
        if not is_unite:
            if not isinstance(v, Addons):
                raise ValidationError("必须为Addons类型")
            for k, v in dict(v).items():
                if k in monitoring and v is None:
                    raise ValidationError(f"{k}插件缺失")
        return v


"""
监控者的配置类 end
"""

"""
监控者类 start
"""
class SystemMonitor(object):
    def __init__(self, options: Options) -> None:
        self.thread_pool = ReusableThreadPool()
        self.unite_async_generator = options.unite_async_generator
        self.monitoring = options.monitoring
        self.addons = options.addons
        self.refresh_interval = options.refresh_interval
        self.channel_queue_max_size = options.channel_queue_max_size
        self.thread_pool_max_workers = options.thread_pool_max_workers
        self.queue = {k: asyncio.Queue(maxsize=self.channel_queue_max_size) for k in self.monitoring}
        self.loop = asyncio.get_running_loop()
        self.is_running = False
        self.exit = True
        self.producer = {}
        self.processor = {}

    def update_queue(self) -> typing.Dict[str, asyncio.Queue]:
        new_queues = {k: asyncio.Queue(maxsize=self.channel_queue_max_size) for k in self.monitoring}
        return new_queues

    def start_thread_pool(self) -> None:
        self.thread_pool.start(max_workers=self.thread_pool_max_workers)
        return None

    def stop_thread_pool(self) -> None:
        self.thread_pool.stop()
        return None

    async def put_memory_queue(self):
        while True:
            memory_snapshot = await self.loop.run_in_executor(self.thread_pool.executor, DataCollector.get_memory_snapshot)
            memory_channel_queue = self.queue.get("memory")
            try:
                await memory_channel_queue.put(memory_snapshot)
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    async def start_memory_monitoring(self) -> None:
        memory_monitoring_task = asyncio.create_task(self.put_memory_queue())
        self.producer["memory"] = memory_monitoring_task
        return None

    async def stop_memory_monitoring(self) -> None:
        memory_monitoring_task = self.producer.get("memory")
        memory_monitoring_task.cancel()
        try:
            await memory_monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            del self.producer["memory"]

    async def put_swap_queue(self):
        while True:
            swap_snapshot = await self.loop.run_in_executor(self.thread_pool.executor, DataCollector.get_swap_snapshot)
            swap_channel_queue = self.queue.get("swap")
            try:
                await swap_channel_queue.put(swap_snapshot)
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    async def start_swap_monitoring(self) -> None:
        swap_monitoring_task = asyncio.create_task(self.put_swap_queue())
        self.producer["swap"] = swap_monitoring_task
        return None

    async def stop_swap_monitoring(self) -> None:
        swap_monitoring_task = self.producer.get("swap")
        swap_monitoring_task.cancel()
        try:
            await swap_monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            del self.producer["swap"]

    async def put_network_queue(self):
        while True:
            network_snapshot = await self.loop.run_in_executor(self.thread_pool.executor, DataCollector.get_network_snapshot)
            network_channel_queue = self.queue.get("network")
            try:
                await network_channel_queue.put(network_snapshot)
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    async def start_network_monitoring(self) -> None:
        network_monitoring_task = asyncio.create_task(self.put_network_queue())
        self.producer["network"] = network_monitoring_task
        return None

    async def stop_network_monitoring(self) -> None:
        network_monitoring_task = self.producer.get("network")
        network_monitoring_task.cancel()
        try:
            await network_monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            del self.producer["network"]

    async def put_cpu_queue(self):
        while True:
            cpu_snapshot = await self.loop.run_in_executor(self.thread_pool.executor, DataCollector.get_cpu_snapshot, self.refresh_interval)
            cpu_channel_queue = self.queue.get("cpu")
            try:
                await cpu_channel_queue.put(cpu_snapshot)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    async def start_cpu_monitoring(self) -> None:
        cpu_monitoring_task = asyncio.create_task(self.put_cpu_queue())
        self.producer["cpu"] = cpu_monitoring_task
        return None

    async def stop_cpu_monitoring(self) -> None:
        cpu_monitoring_task = self.producer.get("cpu")
        cpu_monitoring_task.cancel()
        try:
            await cpu_monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            del self.producer["cpu"]

    async def put_disk_queue(self):
        while True:
            disk_snapshot = await self.loop.run_in_executor(self.thread_pool.executor, DataCollector.get_disk_snapshot)
            disk_channel_queue = self.queue.get("disk")
            try:
                await disk_channel_queue.put(disk_snapshot)
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    async def start_disk_monitoring(self) -> None:
        disk_monitoring_task = asyncio.create_task(self.put_disk_queue())
        self.producer["disk"] = disk_monitoring_task
        return None

    async def stop_disk_monitoring(self) -> None:
        disk_monitoring_task = self.producer.get("disk")
        disk_monitoring_task.cancel()
        try:
            await disk_monitoring_task
        except asyncio.CancelledError:
            pass
        finally:
            del self.producer["disk"]

    async def create_memory_snapshot_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            yield self.queue["memory"].get()

    async def create_swap_snapshot_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            yield self.queue["swap"].get()

    async def create_network_snapshot_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            yield self.queue["network"].get()

    async def create_cpu_snapshot_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            yield self.queue["cpu"].get()

    async def create_disk_snapshot_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            yield self.queue["disk"].get()

    async def create_unite_consumer(self) -> typing.AsyncGenerator:
        while True:
            if self.exit:
                break
            tasks = [self.queue[m].get() for m in self.monitoring]
            yield asyncio.gather(*tasks)

    async def create_consumer(self) -> typing.AsyncGenerator | typing.Dict[str, typing.AsyncGenerator]:
        if self.unite_async_generator:
            return self.create_unite_consumer()
        else:
            async_generators = {
                m: getattr(self, f"create_{m}_snapshot_consumer") for m in self.monitoring
            }
            return async_generators

    async def create_processor(self, _async_generators, /) -> None:
        if self.unite_async_generator:
            func = self.addons.unite
            p = asyncio.create_task(func(item=_async_generators))
            self.processor["unite"] = p
        else:
            for m in self.monitoring:
                addon = getattr(self.addons, m)
                async_generator = _async_generators[m]
                self.processor[m] = asyncio.create_task(addon(item=async_generator))
        return None

    async def del_processor(self) -> None:
        try:
            await asyncio.wait_for(asyncio.gather(*self.processor.values(), return_exceptions=True), timeout=5)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("处理器在返回时被异常阻塞。")
        finally:
            self.processor.clear()
        return None

    async def start(self) -> None:
        # 设置开始标志
        self.is_running, self.exit = True, False
        # 创建异步迭代器
        async_generators = await self.create_consumer()
        # 创建数据处理者
        await self.create_processor(async_generators)
        # 开启线程池
        self.start_thread_pool()
        # 开启生产者
        start_tasks = [getattr(self, f"start_{m}_monitoring")() for m in self.monitoring]
        await asyncio.gather(*start_tasks)
        return None

    async def stop(self) -> None:
        # 设置停止标志
        self.is_running, self.exit = False, True
        # 停止数据处理者
        await self.del_processor()
        # 停止生产者
        stop_tasks = [getattr(self, f"stop_{m}_monitoring")() for m in self.monitoring]
        await asyncio.gather(*stop_tasks)
        # 关闭线程池
        self.stop_thread_pool()
        # 创建新的queue对象
        self.queue = self.update_queue()
        return None
"""
监控者类 end
"""


__all__ = [
    "Addon",
    "Addons",
    "Options",
    "SystemMonitor",
    "ConfigFileEventMonitor",
]

from mitmproxy import master, options, ctx

option = options.Options()
master = master.Master(option)
ctx.master

