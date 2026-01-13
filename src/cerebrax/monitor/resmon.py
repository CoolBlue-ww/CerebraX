from src.cerebrax.common_depend import (
    asyncio,
    typing,
    ThreadPoolExecutor,
)
from src.cerebrax._types import (
    ResourceTypes,
    CommonIterable,
    CollectionMethods,
    Interval,
)
from src.cerebrax.internal import (thread_pool)

class ResourceChangesMonitor(object):
    def __init__(self, call: typing.Callable, aspect: CommonIterable = None, interval: Interval = None) -> None:
        self.aspect = aspect if aspect else ResourceTypes
        self.queues = {k: asyncio.Queue(maxsize=128) for k in self.aspect}
        self.loop = asyncio.get_running_loop()
        self.executor = ThreadPoolExecutor(max_workers=len(self.aspect) + 2)
        self.call = call
        self.interval = (interval, interval) if interval else (0, None)
        self.methods = CollectionMethods
        self.producers = set()
        self.consumer = None
        self.producers_exit = True
        self.consumer_exit = True

    async def put_memory(self):
        while True:
            if self.producers_exit:
                break
            snapshot = await self.loop.run_in_executor(self.executor, self.methods["memory"])
            await self.queues["memory"].put(snapshot)
            await asyncio.sleep(self.interval[0])

    async def put_swap(self):
        while True:
            if self.producers_exit:
                break
            snapshot = await self.loop.run_in_executor(self.executor, self.methods["swap"])
            await self.queues["swap"].put(snapshot)
            await asyncio.sleep(self.interval[0])

    async def put_disk(self):
        while True:
            if self.producers_exit:
                break
            snapshot = await self.loop.run_in_executor(self.executor, self.methods["disk"])
            await self.queues["disk"].put(snapshot)
            await asyncio.sleep(self.interval[0])

    async def put_network(self):
        while True:
            if self.producers_exit:
                break
            snapshot = await self.loop.run_in_executor(self.executor, self.methods["network"])
            await self.queues["network"].put(snapshot)
            await asyncio.sleep(self.interval[0])

    async def put_cpu(self):
        while True:
            if self.producers_exit:
                break
            snapshot = await self.loop.run_in_executor(self.executor, self.methods["cpu"], thread_pool,self.interval[1])
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
        if self.consumer_exit and self.producers_exit:
            self.consumer_exit = False
            self.consumer = asyncio.create_task(self.call(self.get_data()))
            self.producers_exit = False
            for a in self.aspect:
                task = asyncio.create_task(getattr(self, f"put_{a}")())
                self.producers.add(task)

    async def stop(self):
        if not self.producers_exit and not self.consumer_exit:
            self.producers_exit = True
            await asyncio.gather(*self.producers, return_exceptions=True)
            self.consumer_exit = True
            await self.consumer

import time
async def test(x):
    a = time.time()
    count = 0
    total_t = 0
    async for i in x:
        if count > 100000:
            break
        b = time.time()
        total_t += b -a
        # print(f"采集数据样本所花时间：{t * 1000}ms")
        a = b
        count += 1
    print(f"总采样次数：{count-1}，平均单次采样时间为：{(total_t/(count-1)) * 1000}")


async def main():
    rcm = ResourceChangesMonitor(test, None, interval=0.001)
    await rcm.start()
    count = 0
    while count < 10000:
        count += 1
        await asyncio.sleep(1)
    await rcm.stop()

asyncio.run(main())


__all__ = [
    "ResourceChangesMonitor",
]
