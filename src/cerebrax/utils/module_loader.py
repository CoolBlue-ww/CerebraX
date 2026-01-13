from src.cerebrax.common_depend import (
    Path, util,
    asyncio, types
)

def sync_load_module(load_path: str) -> types.ModuleType:
    if not Path(load_path).is_file():
        raise FileNotFoundError(f'{load_path} is not a file')
    load_path = Path(load_path)
    spec = util.spec_from_file_location(
        load_path.name.split(
            sep=".", maxsplit=1)[0],
        str(load_path),
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

async def async_load_module(load_path: str) -> types.ModuleType:
    module = await asyncio.to_thread(sync_load_module, load_path)
    return module


__all__ = [
    "sync_load_module",
    "async_load_module",
]
