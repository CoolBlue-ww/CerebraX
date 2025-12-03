from playwright.async_api import async_playwright
import httpx, asyncio, typing


class PlaywrightClient(object):
    def __init__(self, args: dict) -> None:
        self._args = args
        self._parser = None
        self._async_playwright = None
        self._browser = {}
        self._browser_lookup = set()
        self._context = {}
        self._context_lookup = set()
        self._page = {}
        self._page_lookup = set()

    @property
    def browser(self) -> dict:
        return self._browser

    @property
    def browser_lookup(self) -> set:
        return self._browser_lookup

    @property
    def context(self) -> dict:
        return self._context

    @property
    def context_lookup(self) -> set:
        return self._context_lookup

    @property
    def page(self) -> dict:
        return self._page

    @property
    def page_lookup(self) -> set:
        return self._page_lookup

    @property
    def async_playwright(self) -> typing.Any:
        return self._async_playwright

    async def create_async_playwright(self) -> None:
        """
        创建async_playwright对象
        :return:
        """
        if self._async_playwright is None:
            self._async_playwright = await async_playwright().start()
        return None

    async def create_browser(self) -> None:
        """
        创建browser对象
        :return:
        """
        browser_ids, coro_objs = [], []
        for k, v in self._parser.browser.items():
            core, options = v["core"], v["options"]
            core_obj = getattr(self.async_playwright, core)
            coro = getattr(core_obj, "launch")(**options)
            browser_ids.append(k)
            coro_objs.append(coro)
        browsers = await asyncio.gather(*coro_objs, return_exceptions=True)
        for _id, _browser in zip(browser_ids, browsers):
            self._browser[_id] = _browser
        return None

    async def create_context(self) -> None:
        """
        创建context对象
        :return:
        """
        context_ids, coro_objs = [], []
        for k, v in self._parser.context.items():
            browser_id, options = v["browser_id"], v["options"]
            browser = self.browser[browser_id]
            coro = getattr(browser, "new_context")(**options)
            context_ids.append(k)
            coro_objs.append(coro)
        contexts = await asyncio.gather(*coro_objs, return_exceptions=True)
        for _id, _context in zip(context_ids, contexts):
            self._context[_id] = _context
        return None

    async def create_page(self) -> None:
        """
        创建page对象
        :return:
        """
        page_ids, coro_objs = [], []
        for k, v in self._parser.page.items():
            context_id = v["context_id"]
            context = self.context[context_id]
            coro = getattr(context, "new_page")()
            page_ids.append(k)
            coro_objs.append(coro)
        pages = await asyncio.gather(*coro_objs, return_exceptions=True)
        for _id, _page in zip(page_ids, pages):
            self._page[_id] = _page
        return None

    async def start(self) -> None:
        self._parser = PParser(self._args).parse()
        self._browser_lookup = self._parser.browser_ids
        self._page_lookup = self._parser.context_ids
        self._page_lookup = self._parser.page_ids
        await self.create_async_playwright()
        await self.create_browser()
        await self.create_context()
        await self.create_page()
        return None

    async def stop(self) -> None:
        close_page_tasks = [page.close() for page in self.page.values()]
        close_context_tasks = [context.close() for context in self.context.values()]
        close_browser_tasks = [browser.close() for browser in self.browser.values()]
        await asyncio.gather(*close_page_tasks, return_exceptions=True)
        await asyncio.gather(*close_context_tasks, return_exceptions=True)
        await asyncio.gather(*close_browser_tasks, return_exceptions=True)
        await self.async_playwright.stop()
        self._async_playwright = None
        self._parser = None
        self.browser.clear()
        self.context.clear()
        self.page.clear()
        self._browser_lookup.clear()
        self._context_lookup.clear()
        self._page_lookup.clear()
        return None

    async def add_browser(self, _core: str, _id: str, _options: dict, /) -> None:
        if _id not in self.browser_lookup:
            self._browser_lookup.add(_id)
            core = getattr(self.async_playwright, _core)
            self._browser[_id] = await getattr(core, "launch")(**_options)
        return None

    async def remove_browser(self, _id: str, /) -> None:
        if _id in self.browser_lookup:
            self._browser_lookup.remove(_id)
            _browser = self._browser.pop(_id)
            await _browser.close()
        return None

    async def add_context(self, _browser_id: str, _id, options: dict, /) -> None:
        if _id not in self.context_lookup and _browser_id in self.browser_lookup:
            self._context_lookup.add(_id)
            _context = await getattr(self.browser[_browser_id], "new_context")(**options)
            self._context[_id] = _context
        return None

    async def remove_context(self, _id, /) -> None:
        if _id in self.context_lookup:
            self._context_lookup.remove(_id)
            _context = self.context.pop(_id)
            await _context.close()
        return None

    async def add_page(self, _context_id: str, _id: str, /) -> None:
        if _context_id in self.context_lookup and _id not in self.page_lookup:
            self._page_lookup.add(_id)
            _page = await getattr(self.context[_context_id], "new_page")()
            self._page[_id] = _page
        return None

    async def remove_page(self, _id: str, /) -> None:
        if _id in self.page_lookup:
            self._page_lookup.remove(_id)
            _page = self._page.pop(_id)
            await _page.close()
        return None


class HttpxClient(object):
    def __init__(self, args: dict) -> None:
        self._args = args
        self._parser = None
        self._client_lookup = set()
        self._client = {}

    @property
    def client(self) -> dict:
        return self._client

    @property
    def client_lookup(self) -> set:
        return self._client_lookup

    def add(self, _id: str, _options: dict, /) -> None:
        if _id not in self._client_lookup:
            self._client_lookup.add(_id)
            self._client[_id] = httpx.AsyncClient(**_options)
        return None

    async def remove(self, _id: str, /) -> None:
        if _id in self._client_lookup:
            self._client_lookup.remove(_id)
            _client = self._client.pop(_id)
            await _client.aclose()
        return None

    def create_async_client(self) -> None:
        for k, v in self._parser.client.items():
            self._client[k] = httpx.AsyncClient(**v)
        return None

    def start(self) -> None:
        self._parser = HParser(args=self._args).parse()
        self._client_lookup = self._parser.client_ids
        self.create_async_client()
        return None

    async def stop(self) -> None:
        stop_tasks = []
        for c in self.client.values():
            stop_tasks.append(c.aclose())
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        self._client.clear()
        return None

a = {
    'HttpxClient': {
        'clients': [
            {'client_id': 'id1', 'options': {}},
            {'client_id': 'id2', 'options': {}}
        ]
    }
}

async def main():
    client = HttpxClient(a["HttpxClient"])
    client.start()
    print(client.client_lookup)
    print(client.client)
    client.add('ids_1', {})
    print(client.client_lookup)
    print(client.client)
    await client.stop()
    print(client.client)
    return None

asyncio.run(main())

