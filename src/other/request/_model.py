from pydantic import BaseModel, field_validator, ValidationInfo, ValidationError
from typing import Any, Union, Sequence, Dict, TypedDict, Optional, Literal, List, Pattern, Mapping, Tuple, Callable, Iterable, AsyncIterable, Annotated
from pathlib import Path
import ssl, typing, inspect
from httpx import Timeout, Limits, URL, AsyncBaseTransport, Auth, Request, Proxy, Cookies, Headers, QueryParams
from http.cookiejar import CookieJar


class ProxySettings(BaseModel):
    server: str
    bypass: str | None = None
    username: str | None = None
    password: str | None = None

class BrowserOptions(BaseModel):
    model_config = {'extra': 'forbid'}

    executablePath: Union[str, Path] = None
    channel: str = None
    args: Sequence[str] = None
    ignoreDefaultArgs: Union[bool, Sequence[str]] = None
    handleSIGINT: bool = None
    handleSIGTERM: bool = None
    handleSIGHUP: bool = None
    timeout: float = None
    env: Dict[str, Union[str, float, bool]] = None
    headless: bool = None
    devtools: bool = None
    proxy: ProxySettings = None
    downloadsPath: Union[str, Path] = None
    slowMo: float = None
    tracesDir: Union[str, Path] = None
    chromiumSandbox: bool = None
    firefoxUserPrefs: Dict[str, Union[str, float, bool]] = None


class ViewportSize(BaseModel):
    width: int
    height: int

class Geolocation(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float]

class HttpCredentials(BaseModel):
    username: str
    password: str
    origin: Optional[str]
    send: Optional[Literal["always", "unauthorized"]]

class StorageStateCookie(BaseModel):
    name: str
    value: str
    domain: str
    path: str
    expires: float
    httpOnly: bool
    secure: bool
    sameSite: Literal["Lax", "None", "Strict"]

class LocalStorageEntry(BaseModel):
    name: str
    value: str

class OriginState(BaseModel):
    origin: str
    localStorage: List[LocalStorageEntry]

class StorageState(BaseModel):
    cookies: List[StorageStateCookie]
    origins: List[OriginState]

class ClientCertificate(BaseModel):
    origin: str
    certPath: Optional[Union[str, Path]]
    cert: Optional[bytes]
    keyPath: Optional[Union[str, Path]]
    key: Optional[bytes]
    pfxPath: Optional[Union[str, Path]]
    pfx: Optional[bytes]
    passphrase: Optional[str]

ColorScheme = Literal["dark", "light", "no-preference", "null"]
Contrast = Literal["more", "no-preference", "null"]
ForcedColors = Literal["active", "none", "null"]
ReducedMotion = Literal["no-preference", "null", "reduce"]
ServiceWorkersPolicy = Literal["allow", "block"]
HarMode = Literal["full", "minimal"]
HarContentPolicy = Literal["attach", "embed", "omit"]

class ContextOptions(BaseModel):
    model_config = {'extra': 'forbid'}

    viewport: ViewportSize = None
    screen: ViewportSize = None
    noViewport: bool = None
    ignoreHTTPSErrors: bool = None
    javaScriptEnabled: bool = None
    bypassCSP: bool = None
    userAgent: str = None
    locale: str = None
    timezoneId: str = None
    geolocation: Geolocation = None
    permissions: Sequence[str] = None
    extraHTTPHeaders: Dict[str, str] = None
    offline: bool = None
    httpCredentials: HttpCredentials = None
    deviceScaleFactor: float = None
    isMobile: bool = None
    hasTouch: bool = None
    colorScheme: ColorScheme = None
    reducedMotion: ReducedMotion = None
    forcedColors: ForcedColors = None
    contrast: Contrast = None
    acceptDownloads: bool = None
    defaultBrowserType: str = None
    proxy: ProxySettings = None
    recordHarPath: Union[Path, str] = None
    recordHarOmitContent: bool = None
    recordVideoDir: Union[Path, str] = None
    recordVideoSize: ViewportSize = None
    storageState: Union[StorageState, str, Path] = None
    baseURL: str = None
    strictSelectors: bool = None
    serviceWorkers: ServiceWorkersPolicy = None
    recordHarUrlFilter: Union[Pattern[str], str] = None
    recordHarMode: HarMode = None
    recordHarContent: HarContentPolicy = None
    clientCertificates: List[ClientCertificate] = None

BrowserCore = Literal["chromium", "firefox", "webkit"]

class Browser(BaseModel):
    core: BrowserCore
    options: BrowserOptions

class Context(BaseModel):
    browser: str
    options: ContextOptions

class Page(BaseModel):
    context: str

class PlaywrightClientConfig(BaseModel):
    browsers: Dict[str, Browser]
    contexts: Dict[str, Context]
    pages: Dict[str, Page]

    @field_validator("contexts", mode="before")
    @classmethod
    def _check_browser_ids(cls, v: Dict[str, Context], info: ValidationInfo) -> Dict[str, Context]:
        browser_ids = info.data.get("browser", {}).keys()
        for item in v.values():
            if item["browser"] not in browser_ids:
                raise ValidationError(f"Browser id '{item["browser_id"]}' is invalid.")
        return v

    @field_validator("pages", mode="before")
    @classmethod
    def _check_context_ids(cls, v: Dict[str, Page], info: ValidationInfo) -> Dict[str, Page]:
        context_ids = info.data.get("context", {}).keys()
        for item in v.values():
            if item["context"] not in context_ids:
                raise ValidationError(f"Context id '{item["context_id"]}' is invalid.")
        return v



URLTypes = Union[str, Any]

class _URLTypes(BaseModel):
    item: str

PrimitiveData = Optional[Union[str, int, float, bool]]

QueryParamTypes = Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
    Tuple[Tuple[str, PrimitiveData], ...],
    str,
    bytes,
    Any
]

class _QueryParamTypes(BaseModel):
    item: Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
    Tuple[Tuple[str, PrimitiveData], ...],
    str,
    bytes,
]

HeaderTypes = Union[
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
    Any
]

class _HeaderTypes(BaseModel):
    item: Union[
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
]

CookieTypes = Union[
    Dict[str, str],
    List[Tuple[str, str]],
    Any
]

class _CookieTypes(BaseModel):
    item: Union[
        Dict[str, str],
        List[Tuple[str, str]]
    ]


TimeoutTypes = Union[
    Optional[float],
    Tuple[Optional[float], Optional[float], Optional[float], Optional[float]],
    Any
]

class _TimeoutTypes(BaseModel):
    item: Union[
    Optional[float],
    Tuple[Optional[float], Optional[float], Optional[float], Optional[float]],
]

ProxyTypes = Union[str, Any]

class _ProxyTypes(BaseModel):
    item: str

CertTypes = Optional[Union[str, Tuple[str, str], Tuple[str, str, str]]]

AuthTypes = Union[
    Tuple[Union[str, bytes], Union[str, bytes]],
    Any
]

class _AuthTypes(BaseModel):
    item: Union[
    Tuple[Union[str, bytes], Union[str, bytes]],
]

DEFAULT_TIMEOUT_CONFIG = Timeout(timeout=5.0)
DEFAULT_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
DEFAULT_MAX_REDIRECTS = 20

EventHook = typing.Callable[..., typing.Any]

EventHooks = Optional[typing.Mapping[str, list[EventHook]]]

VerifyTypes = Union[str, bool, Any]

DefaultEncoding = Union[
    str,
    typing.Callable[[bytes], str]
]

class _VerifyTypes(BaseModel):
    item: Union[str, bool]

class HttpxClientOptions(BaseModel):
    model_config = {'extra': 'forbid'}

    auth: AuthTypes = None
    params: QueryParamTypes = None
    headers: HeaderTypes = None
    cookies: CookieTypes = None
    verify: VerifyTypes = True
    cert: CertTypes= None
    http1: bool = True
    http2: bool = False
    proxy: ProxyTypes = None
    mounts: Any = None
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG
    follow_redirects: bool = False
    limits: Any = DEFAULT_LIMITS
    max_redirects: int = DEFAULT_MAX_REDIRECTS
    event_hooks: EventHooks = None
    base_url: URLTypes = ""
    transport: Any = None
    trust_env: bool = True
    default_encoding: DefaultEncoding = "utf-8"

    @field_validator("mounts", mode="before")
    @classmethod
    def _check_mounts(cls, v: Any) -> Any:
        if v is None:
            return v
        elif isinstance(v, typing.Mapping):
            if all(isinstance(i, str) for i in v) and all(isinstance(j, (AsyncBaseTransport, None)) for j in v.values()):
                return v
            raise ValidationError("")
        else:
            raise ValidationError("")

    @field_validator("transport", mode="before")
    @classmethod
    def _check_transport(cls, v: Any) -> Any:
        if isinstance(v, (AsyncBaseTransport, None)):
            return v
        raise ValidationError("")

    @field_validator("base_url", mode="before")
    @classmethod
    def _check_base_url(cls, v: Any) -> Any:
        if isinstance(v, (str, URL, None)):
            return v
        raise ValidationError("base_url 类型错误")

    @field_validator("params", mode="before")
    @classmethod
    def _check_params(cls, v: Any) -> Any:
        if isinstance(v, (QueryParams, None)):
            return v
        else:
            return _QueryParamTypes(item=v).item

    @field_validator("headers", mode="before")
    @classmethod
    def _check_headers(cls, v: Any) -> Any:
        if isinstance(v, (Headers, None)):
            return v
        else:
            return _HeaderTypes(item=v).item

    @field_validator("cookies", mode="before")
    @classmethod
    def _check_cookies(cls, v: Any) -> Any:
        if isinstance(v, (Cookies, CookieJar, None)):
            return v
        else:
            return _CookieTypes(item=v).item

    @field_validator("timeout", mode="before")
    @classmethod
    def _check_timeout(cls, v: Any) -> Any:
        if isinstance(v, Timeout):
            return v
        else:
            return _TimeoutTypes(item=v).item

    @field_validator("proxy", mode="before")
    @classmethod
    def _check_proxy(cls, v: Any) -> Any:
        if isinstance(v, (Proxy, str, URL, None)):
            return v
        raise ValidationError("")

    @field_validator("auth", mode="before")
    @classmethod
    def _check_auth(cls, v: Any) -> Any:
        if isinstance(v, (Auth, None)):
            return v
        elif isinstance(v, Callable):
            sig = inspect.signature(v)
            params = [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
            if len(params) != 1:
                raise ValidationError('middleware must accept exactly 1 positional arg')
            dummy = Request(method="get", url="http://localhost.com")
            try:
                result = None
                if not inspect.iscoroutinefunction(v):
                    result = v(dummy)
            except Exception as e:
                raise ValidationError(f'middleware call failed: {e}')
            if not isinstance(result, Request):
                raise ValidationError('middleware must return a Request instance')
            return v
        else:
            return _AuthTypes(item=v).item

    @field_validator("limits", mode="before")
    @classmethod
    def _check_limits(cls, v: Any) -> Any:
        if isinstance(v, Limits):
            return v
        raise ValidationError("middleware must accept limits")

    @field_validator("verify", mode="before")
    @classmethod
    def _check_verify(cls, v: Any) -> Any:
        if isinstance(v, ssl.SSLContext):
            return v
        else:
            return _VerifyTypes(item=v).item

    @field_validator("default_encoding", mode="before")
    @classmethod
    def _check_default_encoding(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, Callable):
            sig = inspect.signature(v)
            params = [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
            if len(params) != 1:
                raise ValidationError('middleware must accept exactly 1 positional arg')
            dummy = b""
            try:
                result = None
                if not inspect.iscoroutinefunction(v):
                    result = v(dummy)
            except Exception as e:
                raise ValidationError(f'middleware call failed: {e}')
            if not isinstance(result, str):
                raise ValidationError('middleware must return a Request instance')
            return v
        else:
            raise ValidationError('middleware must accept string')

class HttpxClientConfig(BaseModel):
    clients: Dict[str, HttpxClientOptions]

__all__ = [
    "HttpxClientOptions",
    "PlaywrightClientConfig",
    "BrowserOptions",
    "ContextOptions",
]
