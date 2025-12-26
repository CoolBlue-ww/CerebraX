from src.cerebrax.common_depend import dataclass, typing


@dataclass(frozen=True)
class ConfigSnapshot(object):
    lifespan_config: typing.Any = None
    proxy_config: typing.Any = None
