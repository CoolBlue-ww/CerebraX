from src.cerebrax.common_depend import (
    asyncio,
    typing,
)
from src.cerebrax._types import (
    ResourceTypes,
    CommonIterable,
    CollectionMethods,
    Interval,
)


class ResourceChangesMonitor(object):
    def __init__(self, call: typing.Callable, aspect: CommonIterable = None, interval: Interval = None) -> None:
        self.aspect = aspect if aspect else ResourceTypes
        self.queues = {k: asyncio.Queue(maxsize=128) for k in self.aspect}
        self.call = call
        self.interval = 1 if not interval else interval
        self.methods = CollectionMethods
        self.producers = set()
        self.consumer = None
        self.producer_exit = True
        self.consumer_exit = True

    async def create_producer(self, i: str) -> None:
        while True:
            if self.producer_exit:
                break
            snapshot = self.methods[i]()
            try:
                await asyncio.wait_for(self.queues[i].put(snapshot), timeout=1)
            except asyncio.TimeoutError:
                if self.producer_exit:
                    break
            await asyncio.sleep(self.interval)

    async def _create_a_consumer(self, i: str) -> typing.AsyncGenerator[typing.Any, None]:
        queue = self.queues[i]
        while True:
            if self.consumer_exit:
                break
            try:
                item = await asyncio.wait_for(queue.get(), timeout=1)
                yield item
            except asyncio.TimeoutError:
                if queue.empty():
                    break
                else:
                    continue

    def create_consumer(self) -> typing.Dict[str, typing.AsyncGenerator[typing.Any, None]]:
        async_generators = {
            a: self._create_a_consumer(a) for a in self.aspect
        }
        return async_generators


    async def start(self):
        if self.consumer_exit and self.producer_exit:
            self.consumer_exit = False
            self.consumer = asyncio.create_task(self.call(self.create_consumer(), self.stop))
            self.producer_exit = False
            for a in self.aspect:
                task = asyncio.create_task(
                    self.create_producer(a)
                )
                self.producers.add(task)

    async def stop(self):
        if not self.producer_exit and not self.consumer_exit:
            self.producer_exit = True
            print("到这里了")
            await asyncio.gather(*self.producers, return_exceptions=True)
            print("快了快了")
            self.consumer_exit = True
            await self.consumer
            print("这里卡住了？")


async def test(x, z):
    import time
    from aiostream import stream
    a = time.time()
    count = 0
    ts = 0
    async for y in x["cpu"]:
        # if count == 1001:
        #     break
        b = time.time()
        print((b-a)*1000)
        ts += (b-a) * 1000
        a = b
        count += 1
    print(f"采样次数：{count-1}，平均采样时间：{ts/(count-1)}ms")


async def main():
    monitor = ResourceChangesMonitor(test, interval=0.001)
    await monitor.start()
    await asyncio.sleep(3)
    # print(monitor.producer_exit, monitor.consumer_exit)
    await monitor.stop()

# 采样次数：10000，平均采样时间：2.5746946573257445ms
# 采样次数：10000，平均采样时间：2.5925132989883424ms
asyncio.run(main())

__all__ = [
    "ResourceChangesMonitor",
]
