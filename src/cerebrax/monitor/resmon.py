from src.cerebrax.common_depend import (
    asyncio,
    typing,
)
from src.cerebrax._types import (
    ResourceTypes,
    CommonIterable,
    ResourceMapping,
    Interval,
)

class ResourceChangesMonitor(object):
    def __init__(self, call: typing.Callable, aspect: CommonIterable = None, interval: Interval = None) -> None:
        self.aspect = aspect if aspect else ResourceTypes
        self.queues = {k: asyncio.Queue(maxsize=128) for k in self.aspect}
        self.call = call
        self.interval = interval
        self.mapping = ResourceMapping
        self.producers = set()
        self.consumer = None
        self.producer_exit = True
        self.consumer_exit = True

    async def put_memory(self):
        while True:
            if self.producer_exit:
                break
            snapshot = self.mapping["memory"]()
            await self.queues["memory"].put(snapshot)
            await asyncio.sleep(self.interval)

    async def put_swap(self):
        while True:
            if self.producer_exit:
                break
            snapshot = self.mapping["swap"]()
            await self.queues["swap"].put(snapshot)
            await asyncio.sleep(self.interval)

    async def put_disk(self):
        while True:
            if self.producer_exit:
                break
            snapshot = self.mapping["disk"]()
            await self.queues["disk"].put(snapshot)
            await asyncio.sleep(self.interval)

    async def put_network(self):
        while True:
            if self.producer_exit:
                break
            snapshot = self.mapping["network"]()
            await self.queues["network"].put(snapshot)
            await asyncio.sleep(self.interval)

    async def put_cpu(self):
        while True:
            if self.producer_exit:
                break
            snapshot = await asyncio.to_thread(self.mapping["cpu"], self.interval)
            await self.queues["cpu"].put(snapshot)

    async def get_data(self) -> typing.AsyncGenerator[typing.Any, None]:
        while True:
            if self.consumer_exit:
                break
            try:
                results = await asyncio.wait_for(asyncio.gather(
                    *[q.get() for q in self.queues.values()],
                    return_exceptions=True
                    ),
                    timeout=10,
                )
                data = {k: v for k, v in zip(self.aspect, results)}
                yield data
            except asyncio.TimeoutError:
                break

    async def start(self):
        self.consumer_exit = False
        self.consumer = asyncio.create_task(self.call(self.get_data()))
        self.producer_exit = False
        for a in self.aspect:
            task = asyncio.create_task(getattr(self, f"put_{a}")())
            self.producers.add(task)

    async def stop(self):
        self.producer_exit = True
        await asyncio.gather(*self.producers, return_exceptions=True)
        self.consumer_exit = True
        await self.consumer


__all__ = [
    "ResourceChangesMonitor",
]
