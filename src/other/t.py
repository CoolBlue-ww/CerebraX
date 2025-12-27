
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
