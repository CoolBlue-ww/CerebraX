from src.cerebrax.common_depend import dataclass, typing


@dataclass(frozen=True)
class ConfigSnapshot(object):
    lifespan_config: typing.Any = None
    proxy_config: typing.Any = None


@dataclass(frozen=False)
class Shared(object):
    pass

@dataclass(frozen=False)
class Toolkit(object):
    pass


__all__ = [
    "ConfigSnapshot",
    "Shared",
    "Toolkit",
]