from src.cerebrax.common_depend import (
    asyncio,
    typing,
    uuid,
)
from src.cerebrax._types import (
    ResourceTypes,
    CommonIterable,
    CollectionMethods,
    Interval,
)


class AsyncGeneratorCompatibleLayer(object):
    def __init__(self,
                 async_generator: typing.AsyncGenerator[typing.Any, None],
                 communication_queue: asyncio.Queue,
                 async_event: asyncio.Event,
                 ) -> None:
        self._async_generator = async_generator
        self._communication_queue = communication_queue
        self._async_event = async_event

    def __aiter__(self):
        return self._async_generator

    async def __anext__(self):
        async for item in self._async_generator:
            yield item

    def pause(self):
        self._async_event.clear()

    def resume(self):
        self._async_event.set()

    def clear(self):
        while not self._communication_queue.empty():
            try:
                self._communication_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

class ResourceChangesMonitor(object):
    def __init__(self, call: typing.Callable, aspect: CommonIterable = None, interval: Interval = None) -> None:
        self.aspect = aspect if aspect else ResourceTypes
        self.queues = {k: asyncio.Queue(maxsize=128) for k in self.aspect}
        self.events = {k: asyncio.Event() for k in self.aspect}
        self._event_to_set()
        self.call = call
        self.interval = 1 if not interval else interval
        self.methods = CollectionMethods
        self.producers = set()
        self.consumer = None
        self.running = False

    def _event_to_set(self):
        for e in self.events.values():
            e.set()

    async def _create_a_producer(self, i: str) -> None:
        queue, event = self.queues[i], self.events[i]
        while True:
            if not event.is_set():
                await event.wait()
            snapshot = self.methods[i]()
            try:
                await queue.put(snapshot)
            except asyncio.CancelledError:
                raise asyncio.CancelledError()
            await asyncio.sleep(self.interval)

    async def create_producer(self):
        for a in self.aspect:
            task = asyncio.create_task(self._create_a_producer(a))
            self.producers.add(task)

    async def _create_a_consumer(self, i: str) -> typing.AsyncGenerator[typing.Any, None]:
        queue, event = self.queues[i], self.events[i]
        while True:
            if not event.is_set():
                await event.wait()
            try:
                item = await queue.get()
                yield item
            except asyncio.CancelledError:
                raise asyncio.CancelledError()

    def create_consumer(self):
        async_generators = {
            a: AsyncGeneratorCompatibleLayer(
                async_generator=self._create_a_consumer(a),
                communication_queue=self.queues[a],
                async_event=self.events[a],
            ) for a in self.aspect}
        self.consumer = asyncio.create_task(self.call(async_generators))


    async def start(self):
        if not self.running:
            self.create_consumer()
            await self.create_producer()
            self.running = True

    async def stop(self):
        if self.running:
            for p in self.producers:
                try:
                    p.cancel()
                    await p
                except asyncio.CancelledError:
                    pass
            self.producers.clear()
            self.consumer = None
            self.running = False


__all__ = [
    "ResourceChangesMonitor",
]
