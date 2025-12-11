import tomllib, asyncio, pathlib, typing
from src.cerebrax.tools.type_and_module import (
    LifespanConfig,
    ProxyConfig,
)


class ConfigLoader(object):
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise TypeError("path must be a string.")
        if not path.endswith(".toml"):
            raise TypeError("path must be a toml file.")
        self._path = path
        self._cfg = {}

    @property
    def cfg(self) -> typing.Dict[str, typing.Any]:
        return self._cfg

    def sync_load(self) -> typing.Dict[str, typing.Any]:
        obj = pathlib.Path(self._path).resolve()
        if obj.is_file():
            with obj.open(mode="rb") as f:
                self._cfg = tomllib.load(f)
                return self.cfg
        return {}

    async def async_load(self) -> typing.Dict[str, typing.Any]:
        cfg = await asyncio.to_thread(self.sync_load)
        return cfg


class ConfigParser(object):
    def __init__(self, cfg: typing.Dict[str, typing.Any]) -> None:
        self.cfg = cfg
        self._lifespan_cfg = None
        self._proxy_cfg = None

    @property
    def lifespan_cfg(self) -> typing.Optional[LifespanConfig]:
        return self._lifespan_cfg

    @property
    def proxy_cfg(self) -> typing.Optional[ProxyConfig]:
        return self._proxy_cfg

    def parse_lifespan_cfg(self) -> None:
        _cfg = self.cfg.get("Lifespan", {})
        self._lifespan_cfg = LifespanConfig(**_cfg)
        return None

    def parse_proxy_cfg(self) -> None:
        _cfg = self.cfg.get("Proxy", {})
        self._proxy_cfg = ProxyConfig(**_cfg)
        return None

    def parse(self) -> "ConfigParser":
        self.parse_lifespan_cfg()
        self.parse_proxy_cfg()
        return self


__all__ = [
    "ConfigLoader",
    "ConfigParser",
]
