import inspect, typing
import pickle


def v(a: int, b: str):
    return None

sig = inspect.signature(v)
params = [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]

print(sig)
print(params)

async def pp(): pass

def p_p(): pass

if isinstance(pp, typing.Callable) and isinstance(p_p, typing.Callable):
    print(True)

print(inspect.iscoroutinefunction(pp))

def tt() -> None:
    print("你好世界")
    return None

d = pickle.dumps(tt)
print(d)
