"""
配置文件监控
"""
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import asyncio, typing, time

"""
监控目标文件并返回事件流迭代器
"""
class ConfigFileEventHandler(FileSystemEventHandler):
    def __init__(self,
                 key_path: str,
                 loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue
                 ) -> None:
        self.key_path = key_path
        self.loop = loop
        self.queue = queue
        self.exit = True

    def on_modified(self, event) -> None:
        if not event.is_directory:
            file_path = event.src_path
            if file_path == self.key_path:
                future = asyncio.run_coroutine_threadsafe(
                    self.put_new_item(item=file_path), loop=self.loop
                )
                try:
                    future.result(timeout=5)
                except asyncio.TimeoutError:
                    pass
        return None

    async def put_new_item(self, item: str) -> None:
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            self.queue.get_nowait()
            await self.put_new_item(item)
        return None

    async def get_new_item(self) -> str:
        item = await self.queue.get()
        return item

    async def event_floe(self) -> typing.AsyncGenerator:
        self.exit = False
        while True:
            if self.exit:
                break
            item = await self.get_new_item()
            yield item


class ConfigFileEventMonitor(object):
    def __init__(self,
                 path: str,
                 name: str,
                 reload: typing.Callable,
                 shared_instances) -> None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            self.handler = ConfigFileEventHandler(
                key_path=f"{path}/{name}",  # 要监控的配置文件路径
                loop=loop,  # 当前正在运行的事件循环
                queue=asyncio.Queue(maxsize=1),  # 绑定当前事件循环的队列
            )
        else:
            raise RuntimeError("Loop is not running")
        self.observer = Observer()
        self.path = path
        self.reload = reload
        self.shared_instances = shared_instances
        self.monitoring_task = None

    def start(self) -> None:
        self.observer.schedule(self.handler, path=self.path, recursive=True)
        self.observer.start()
        self.monitoring_task = asyncio.create_task(
            self.reload(
                event_flow=self.handler.event_floe(),
                shared_instance=self.shared_instances
            )
        )
        return None

    async def stop(self) -> None:
        self.handler.exit = True
        try:
            await asyncio.wait_for(self.monitoring_task, timeout=5)
        except asyncio.TimeoutError:
            pass
        finally:
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
        return None


__all__ = [
    "ConfigFileEventMonitor"
]
