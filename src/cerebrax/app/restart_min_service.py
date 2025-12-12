import httpx, asyncio


class RestartMinService(object):
    def __init__(self, host, base_cfg_parser, new_cfg_parser) -> None:
        self.host = host
        self.base_cfg_parser = base_cfg_parser
        self.new_cfg_parser = new_cfg_parser
        self. shared_async_client = httpx.AsyncClient()

    async def restart(self) -> None:
        base_proxy_cfg = self.base_cfg_parser.proxy_cfg
        # -----------------------------------------------
        new_proxy_cfg = self.new_cfg_parser.proxy_cfg

        # -----------------------------------------------
        wait_restart = []
        if base_proxy_cfg != new_proxy_cfg:
            wait_restart.append(self.host + "/proxy/restart")

        # -----------------------------------------------

        restart_tasks = [
            self.shared_async_client.post(url=url) for url in wait_restart
        ]
        await asyncio.gather(*restart_tasks, return_exceptions=True)
        return None

