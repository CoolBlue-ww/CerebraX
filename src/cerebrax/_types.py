from src.cerebrax.common_depend import (
    docker,
    typing,
)


TIME = typing.Union[int, float]
DefaultLifeCycle: TIME = 0
DefaultWaitForExit: TIME = 0
DefaultExitTimeout: TIME = 10


DefaultStartupCommand: typing.List[str] = ["mitmdump"]
AutoStart: bool = False
AdaptPattern: bool = False
FallbackPattern: str = "mitmdump"
Patterns: typing.Set[str] = {"mitmdump", "mitmproxy", "mitmweb"}

DockerImageList = typing.Union[typing.List, typing.Dict]
DefaultContainerQuery: str = "CerebraX-OCR"
ContainerRunArgs = typing.Optional[typing.Dict[str, typing.Any]]
DefaultContainerRunArgs: typing.Dict[str, typing.Any] = {
    "image": "ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-vl:latest",
    "name": "CerebraX-OCR",
    "command": "paddlex_genai_server "
            "--model_name PaddleOCR-VL-0.9B "
            "--model_dir /opt/models/PaddleOCR-VL-0.9B "   # 镜像内部路径
            "--backend vllm "
            "--host 0.0.0.0 --port 8118 "
            "--gpu-memory-utilization 0.8 "
            "--max-model-len 8192 "
            "--trust-remote-code",
    "device_requests": [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
    "ports": {'8118/tcp': 8118},
    "shm_size": '16g',          # vLLM 必开
    "detach": True
}

