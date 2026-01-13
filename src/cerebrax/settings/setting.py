from src.cerebrax.utils import (
    module_loader,
)
from src.cerebrax.common_depend import (
    types,
    httpx,
    typing,
)


class QueryHttpxClient(object):
    def __init__(self, module: types.ModuleType) -> None:
        self.module = module

    def query(self) -> typing.Dict:
        """
        {
            "direct": {},
            "proxy": {},
        }
        :return:
        """
        if hasattr(self.module, "httpx_client") and isinstance(self.module.httpx_client, typing.Dict):
            httpx_client = self.module.httpx_client
            if "direct":

            else:
                raise KeyError("direct and proxy is None.")
        else:
            raise KeyError("httpx_client is None.")


