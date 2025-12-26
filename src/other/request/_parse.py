class PParser(object):
    def __init__(self, args: dict) -> None:
        """
        传入的是PlaywrightClient参数的字典
        :param args:
        """
        self._args = args
        self._browsers = {}
        self._contexts = {}
        self._pages = {}
        self._browser_ids = set()
        self._context_ids = set()
        self._page_ids = set()
        self._parse()

    @property
    def browsers(self) -> dict:
        return self._browsers

    @property
    def contexts(self) -> dict:
        return self._contexts

    @property
    def pages(self) -> dict:
        return self._pages

    @property
    def browser_ids(self) -> set:
        return self._browser_ids

    @property
    def context_ids(self) -> set:
        return self._context_ids

    @property
    def page_ids(self) -> set:
        return self._page_ids

    def _get_items(self) -> tuple:
        browsers = self._args["browsers"]
        contexts = self._args["contexts"]
        pages = self._args["pages"]
        return browsers, contexts, pages

    def _get_ids(self) -> tuple:
        browser_ids = set(self._browsers.keys())
        context_ids = set(self._contexts.keys())
        page_ids = set(self._pages.keys())
        return browser_ids, context_ids, page_ids

    def _parse(self) -> None:
        self._browsers, self._contexts, self._pages = self._get_items()
        self._browser_ids, self._context_ids, self._page_ids = self._get_ids()
        return None


class HParser(object):
    def __init__(self, args: dict) -> None:
        self._clients = args
        self._client_ids = set(args.keys())

    @property
    def client_ids(self) -> set:
        return self._client_ids

    @property
    def clients(self) -> dict:
        return self._clients


a = {
    'browsers': {
        'browser_1': {
            'core': 'chromium',
            'options': {'headless': True}}
    },
    'contexts': {
        'context_1': {
            'browser': 'browser_1',
            'options': {'viewport': {'width': 10, 'height': 10}}
        }
    },
    'pages': {
        'page_1': {'context': 'context_1'}
    }
}

b = {'client_1': {'a': 10, 'b': 10}}

__all__ = [
    "PParser",
    "HParser",
]
