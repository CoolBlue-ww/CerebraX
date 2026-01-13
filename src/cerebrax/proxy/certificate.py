from src.cerebrax.common_depend import (
    typing,
    platform as pf,
    aiopath,
    httpx
)
from src.cerebrax.internal import (
    httpx_proxy_client as client,
)
from src.cerebrax._types import (
    Platforms,
    OtherPlatformFormat,
)

class CertificateInstaller(object):
    __slots__ = ('url', 'proxy', 'certificate_links')

    def __init__(self, proxy: str = "http://localhost:8080") -> None:
        self.proxy = proxy
        self.certificate_links = {
            "windows": "http://mitm.it/cert/p12",
            "linux": "http://mitm.it/cert/pem",
            "ios": "http://mitm.it/cert/pem",
            "macos": "http://mitm.it/cert/pem",
            "android": "http://mitm.it/cert/cer",
            "firefox": "http://mitm.it/cert/pem",
            "other-platforms": {
                "p12": "http://mitm.it/cert/p12",
                "pem": "http://mitm.it/cert/pem",
            }
        }

    async def install(self,
                      platform: typing.Optional[Platforms] = None,
                      other_platform_format: typing.Optional[OtherPlatformFormat] = None,
                      save_dir: typing.Optional[str] = None,
                      ) -> str:
        cert_platform = platform or pf.system()
        if cert_platform and cert_platform.lower() not in self.certificate_links.keys():
            raise ValueError(
                f'Platform "{platform}" is not supported.'
                f' The platform must be "windows", "linux", "ios", "macos", "android", "firefox" or "other-platforms".'
            )
        if cert_platform == 'Darwin':
            cert_platform = 'macOS'
        cert_save_dir = aiopath.AsyncPath(save_dir)
        if not await cert_save_dir.is_dir():
            cert_save_dir.mkdir(parents=True, exist_ok=True)
        cert_url = self.certificate_links[cert_platform.lower()]
        if isinstance(cert_url, typing.Dict):
            if not other_platform_format or other_platform_format not in {'pem', 'p12'}:
                cert_url = cert_url["pem"]
            else:
                cert_url = cert_url[other_platform_format]
        cert_file = cert_save_dir.joinpath(
            f'mitmproxy-ca-cert-{cert_platform.lower()}.{cert_url.rsplit(
                sep="/", maxsplit=1)[-1]}'
        )
        try:
            response = await client.get(url=cert_url)
            response.raise_for_status()
            data = response.text if cert_file.suffix == "/pem" else response.content
            is_bytes = isinstance(data, bytes)
            async with cert_file.open(
                    mode = "wb" if is_bytes else "wt",
                    encoding = None if is_bytes else "ascii",
            ) as file:
                await file.write(data)
        except httpx.HTTPError:
            raise httpx.HTTPError("Proxy service not enabled.")
        return str(cert_file)

__all__ = [
    'CertificateInstaller',
]
