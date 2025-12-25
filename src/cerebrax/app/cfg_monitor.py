"""
配置文件监控
"""
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import asyncio, typing

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
            self.queue.put_nowait(item)  # 队列已经满
        except asyncio.QueueFull:
            self.queue.get_nowait()  # 丢弃过期数据
            await self.put_new_item(item)  # 回调放入新的数据（防止其他地方意外往队列里面传数据）
        return None

    async def get_new_item(self) -> str:
        item = await self.queue.get()
        return item

    # 只是外部可以使用的异步迭代器
    async def event_flow(self) -> typing.AsyncGenerator:
        self.exit = False
        while True:
            if self.exit:
                break
            item = await self.get_new_item()
            yield item


class ConfigFileEventMonitor(object):
    def __init__(self,
                 path: str,  # 监控目录
                 name: str,  # 监控的关键文件名字
                 reload: typing.Callable,  # 文件变更后的做法
                 shared_instances  # 共享实例，里面存在可使用的对象
                 ) -> None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            self.handler = ConfigFileEventHandler(
                key_path=f"{path}/{name}",  # 要监控的配置文件路径
                loop=loop,  # 当前正在运行的事件循环
                queue=asyncio.Queue(maxsize=1),  # 绑定当前事件循环的队列，单元素缓存保持最新
            )
        else:
            raise RuntimeError("Loop is not running")
        self.observer = Observer()
        self.path = path
        self.reload = reload
        self.shared_instances = shared_instances
        self.task = None

    def start(self) -> None:
        if self.handler.exit:
            self.handler.exit = False
            self.observer.schedule(self.handler, path=self.path, recursive=True)
            self.observer.start()
            self.task = asyncio.create_task(
                self.reload(
                    event_flow=self.handler.event_flow(),
                    shared_instance=self.shared_instances
                )
            )
        return None

    async def stop(self) -> None:
        if not self.handler.exit:
            self.handler.exit = True
            try:
                await asyncio.wait_for(self.task, timeout=10)
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
