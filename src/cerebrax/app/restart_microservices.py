import httpx, asyncio, typing


class RestartMicroservices(object):
    def __init__(self, authority, base_cfg_parser, new_cfg_parser) -> None:
        self.authority = authority
        self.base_cfg_parser = base_cfg_parser
        self.new_cfg_parser = new_cfg_parser
        self. shared_async_client = httpx.AsyncClient()

    def restart_proxy(self, l: typing.List) -> None:
        base_proxy_cfg = self.base_cfg_parser.proxy_cfg
        # -----------------------------------------------
        new_proxy_cfg = self.new_cfg_parser.proxy_cfg
        # -----------------------------------------------
        if base_proxy_cfg != new_proxy_cfg:
            l.append(self.authority + "/proxy/restart")
        return None

    async def restart(self) -> None:
        wait_restart = []  # 全部等待重启的任务
        # -----------------------------------------------


        # -----------------------------------------------

        restart_tasks = [
            self.shared_async_client.post(url=url) for url in wait_restart
        ]
        await asyncio.gather(*restart_tasks, return_exceptions=True)  # 发送重启请求
        return None



