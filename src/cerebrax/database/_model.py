from pydantic import BaseModel, field_validator, ValidationError
import typing, ssl as _ssl, OpenSSL
from redis.retry import Retry
from redis.backoff import ExponentialWithJitterBackoff
from redis.cache import CacheConfig
from redis.event import EventDispatcher
from redis.credentials import CredentialProvider
from redis.maint_notifications import MaintNotificationsConfig
from redis.cache import CacheInterface
from redis.utils import get_lib_version
from redis.connection import ConnectionPool


DefaultRetry = Retry(backoff=ExponentialWithJitterBackoff(base=1, cap=10), retries=3)

class SyncRedisOptions(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: typing.Optional[str] = None
    socket_timeout: typing.Optional[float] = None
    socket_connect_timeout: typing.Optional[float] = None
    socket_keepalive: typing.Optional[bool] = None
    socket_keepalive_options: typing.Optional[typing.Mapping[int, typing.Union[int, bytes]]] = None
    connection_pool: typing.Any = None
    unix_socket_path: typing.Optional[str] = None
    encoding: str = "utf-8"
    encoding_errors: str = "strict"
    decode_responses: bool = False
    retry_on_timeout: bool = False
    retry: typing.Any = DefaultRetry
    retry_on_error: typing.Optional[typing.List[typing.Type[Exception]]] = None
    ssl: bool = False
    ssl_keyfile: typing.Optional[str] = None
    ssl_certfile: typing.Optional[str] = None
    ssl_cert_reqs: typing.Union[str, typing.Any] = "required"
    ssl_include_verify_flags: typing.Any = None
    ssl_exclude_verify_flags: typing.Any = None
    ssl_ca_certs: typing.Optional[str] = None
    ssl_ca_path: typing.Optional[str] = None
    ssl_ca_data: typing.Optional[str] = None
    ssl_check_hostname: bool = True
    ssl_password: typing.Optional[str] = None
    ssl_validate_ocsp: bool = False
    ssl_validate_ocsp_stapled: bool = False
    ssl_ocsp_context: typing.Any = None
    ssl_ocsp_expected_cert: typing.Optional[str] = None
    ssl_min_version: typing.Any = None
    ssl_ciphers: typing.Optional[str] = None
    max_connections: typing.Optional[int] = None
    single_connection_client: bool = False
    health_check_interval: int = 0
    client_name: typing.Optional[str] = None
    lib_name: typing.Optional[str] = "redis-py"
    lib_version: typing.Optional[str] = get_lib_version()
    username: typing.Optional[str] = None
    redis_connect_func: typing.Optional[typing.Callable[[], None]] = None
    credential_provider: typing.Any = None
    protocol: typing.Optional[int] = 2
    cache: typing.Any = None
    cache_config: typing.Any = None
    event_dispatcher: typing.Any = None
    maint_notifications_config: typing.Any = None

    @field_validator("retry", mode="before")
    @classmethod
    def _check_retry(cls, v: typing.Any) -> typing.Any:
        if isinstance(v, Retry):
            return v
        raise ValidationError("")

    @field_validator("ssl_include_verify_flags", mode="before")
    @classmethod
    def _check_ssl_include_verify_flags(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, typing.List):
            if all(isinstance(i, _ssl.VerifyFlags) for i in v):
                return v
            else:
                raise ValidationError("")
        else:
            raise ValidationError("")

    @field_validator("ssl_exclude_verify_flags", mode="before")
    @classmethod
    def _check_ssl_exclude_verify_flags(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, typing.List):
            if all(isinstance(i, _ssl.VerifyFlags) for i in v):
                return v
            else:
                raise ValidationError("")
        else:
            raise ValidationError("")

    @field_validator("ssl_ocsp_context", mode="before")
    @classmethod
    def _check_ssl_ocsp_context(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, OpenSSL.SSL.Context):
            return v
        else:
            raise ValidationError("")

    @field_validator("ssl_min_version", mode="before")
    @classmethod
    def _check_ssl_min_version(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, _ssl.TLSVersion):
            return v
        else:
            raise ValidationError("")

    @field_validator("credential_provider", mode="before")
    @classmethod
    def _check_credential_provider(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, CredentialProvider):
            return v
        else:
            raise ValidationError("")

    @field_validator("cache", mode="before")
    @classmethod
    def _check_cache(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, CacheInterface):
            return v
        else:
            raise ValidationError("")

    @field_validator("cache_config", mode="before")
    @classmethod
    def _check_cache_config(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, CacheConfig):
            return v
        else:
            raise ValidationError("")

    @field_validator("event_dispatcher", mode="before")
    @classmethod
    def _check_event_dispatcher(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, EventDispatcher):
            return v
        else:
            raise ValidationError("")

    @field_validator("maint_notifications_config", mode="before")
    @classmethod
    def _check_maint_notifications_config(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, MaintNotificationsConfig):
            return v
        else:
            raise ValidationError("")

    @field_validator("ssl_cert_reqs", mode="before")
    @classmethod
    def _check_ssl_cert_reqs(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, (str, _ssl.VerifyMode)):
            return v
        else:
            raise ValidationError("")

    @field_validator("connection_pool", mode="before")
    @classmethod
    def _check_connection_pool(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, ConnectionPool):
            return v
        else:
            raise ValidationError("")



class AsyncRedisOptions(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: typing.Union[str, int] = 0
    password: typing.Optional[str] = None
    socket_timeout: typing.Optional[float] = None
    socket_connect_timeout: typing.Optional[float] = None
    socket_keepalive: typing.Optional[bool] = None
    socket_keepalive_options: typing.Optional[typing.Mapping[int, typing.Union[int, bytes]]] = None
    connection_pool: typing.Any = None
    unix_socket_path: typing.Optional[str] = None
    encoding: str = "utf-8"
    encoding_errors: str = "strict"
    decode_responses: bool = False
    retry_on_timeout: bool = False
    retry: typing.Any = DefaultRetry
    retry_on_error: typing.Optional[list] = None
    ssl: bool = False
    ssl_keyfile: typing.Optional[str] = None
    ssl_certfile: typing.Optional[str] = None
    ssl_cert_reqs: typing.Any = "required"
    ssl_include_verify_flags: typing.Any = None
    ssl_exclude_verify_flags: typing.Any = None
    ssl_ca_certs: typing.Optional[str] = None
    ssl_ca_data: typing.Optional[str] = None
    ssl_check_hostname: bool = True
    ssl_min_version: typing.Any = None
    ssl_ciphers: typing.Optional[str] = None
    max_connections: typing.Optional[int] = None
    single_connection_client: bool = False
    health_check_interval: int = 0
    client_name: typing.Optional[str] = None
    lib_name: typing.Optional[str] = "redis-py"
    lib_version: typing.Optional[str] = get_lib_version()
    username: typing.Optional[str] = None
    auto_close_connection_pool: typing.Optional[bool] = None
    redis_connect_func: typing.Any = None
    credential_provider: typing.Any = None
    protocol: typing.Optional[int] = 2
    event_dispatcher: typing.Any = None

    @field_validator("retry", mode="before")
    @classmethod
    def _check_retry(cls, v: typing.Any) -> typing.Any:
        if isinstance(v, Retry):
            return v
        raise ValidationError("")

    @field_validator("connection_pool", mode="before")
    @classmethod
    def _check_connection_pool(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, ConnectionPool):
            return v
        else:
            raise ValidationError("")

    @field_validator("ssl_cert_reqs", mode="before")
    @classmethod
    def _check_ssl_cert_reqs(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, (str, _ssl.VerifyMode)):
            return v
        else:
            raise ValidationError("")

    @field_validator("ssl_include_verify_flags", mode="before")
    @classmethod
    def _check_ssl_include_verify_flags(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, typing.List):
            if all(isinstance(i, _ssl.VerifyFlags) for i in v):
                return v
            else:
                raise ValidationError("")
        else:
            raise ValidationError("")

    @field_validator("ssl_exclude_verify_flags", mode="before")
    @classmethod
    def _check_ssl_exclude_verify_flags(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, typing.List):
            if all(isinstance(i, _ssl.VerifyFlags) for i in v):
                return v
            else:
                raise ValidationError("")
        else:
            raise ValidationError("")

    @field_validator("ssl_min_version", mode="before")
    @classmethod
    def _check_ssl_min_version(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, _ssl.TLSVersion):
            return v
        else:
            raise ValidationError("")

    @field_validator("credential_provider", mode="before")
    @classmethod
    def _check_credential_provider(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, CredentialProvider):
            return v
        else:
            raise ValidationError("")

    @field_validator("event_dispatcher", mode="before")
    @classmethod
    def _check_event_dispatcher(cls, v: typing.Any) -> typing.Any:
        if v is None:
            return v
        elif isinstance(v, EventDispatcher):
            return v
        else:
            raise ValidationError("")

__all__ = [
    "SyncRedisOptions",
    "AsyncRedisOptions",
]
