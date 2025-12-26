from src.cerebrax.common_depend import tomllib, asyncio, pathlib, typing
from src.cerebrax._container import ConfigSnapshot
from src.cerebrax._models import (
LifespanConfig,
ProxyConfig,
)

class Loader(object):
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise TypeError("path must be a string.")
        if not path.endswith(".toml"):
            raise TypeError("path must be a toml file.")
        self._path = path
        self._data = {}

    @property
    def data(self) -> typing.Dict[str, typing.Any]:
        return self._data

    def sync_load(self) -> typing.Dict[str, typing.Any]:
        obj = pathlib.Path(self._path).resolve()
        if obj.is_file():
            with obj.open(mode="rb") as f:
                self._data = tomllib.load(f)
                return self.data
        return {}

    async def async_load(self) -> typing.Dict[str, typing.Any]:
        cfg = await asyncio.to_thread(self.sync_load)
        return cfg


class Parser(object):
    def __init__(self) -> None:
        self.config = None
        self._lifespan_config = None
        self._proxy_config = None

    @property
    def lifespan_config(self) -> typing.Optional[LifespanConfig]:
        return self._lifespan_config

    @property
    def proxy_config(self) -> typing.Optional[ProxyConfig]:
        return self._proxy_config

    def parse_lifespan_config(self) -> None:
        _cfg = self.config.get("Lifespan", {})
        self._lifespan_config = LifespanConfig(**_cfg)
        return None

    def parse_proxy_config(self) -> None:
        _cfg = self.config.get("Proxy", {})
        self._proxy_config = ProxyConfig(**_cfg)
        return None

    def parse(self, config: typing.Dict[str, typing.Any]) -> "Parser":
        self.config = config
        self.parse_lifespan_config()
        self.parse_proxy_config()
        return self


class Config(object):
    def __init__(self, path: str) -> None:
        self._loader = Loader(path)
        self._parser = Parser()

    def get(self) -> ConfigSnapshot:
        cfg = self._loader.sync_load()
        parser = self._parser.parse(config=cfg)
        config_snapshot =  ConfigSnapshot(
            lifespan_config=parser.lifespan_config,
            proxy_config=parser.proxy_config
        )
        return config_snapshot

    async def async_get(self) -> ConfigSnapshot:
        cfg = await self._loader.async_load()
        parser = self._parser.parse(config=cfg)
        config_snapshot = ConfigSnapshot(
            lifespan_config=parser.lifespan_config,
            proxy_config=parser.proxy_config
        )
        return config_snapshot


__all__ = [
    "Config",
]
