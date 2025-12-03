import tomllib, asyncio, pathlib, typing


class Config(object):
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise TypeError("path must be a string.")
        self._path = path
        self._data = {}

    @property
    def data(self) -> typing.Dict[str, typing.Any]:
        return self._data

    @property
    def playwright_client(self) -> typing.Dict[str, typing.Any]:
        return self.data.get("PlaywrightClient", {})

    @property
    def httpx_client(self) -> typing.Dict[str, typing.Any]:
        return self.data.get("HttpxClient", {})

    def sync_load(self) -> typing.Dict[str, typing.Any]:
        obj = pathlib.Path(self._path).resolve()
        if obj.is_file():
            with obj.open(mode="rb") as f:
                self._data = tomllib.load(f)
                return self.data
        return {}

    async def async_load(self) -> typing.Dict[str, typing.Any]:
        data = await asyncio.to_thread(self.sync_load)
        return data

__all__ = ["Config"]
