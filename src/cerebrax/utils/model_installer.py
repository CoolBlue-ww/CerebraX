from modelscope.hub.snapshot_download import snapshot_download
import typing

ModelsType = typing.Union[
    typing.Tuple[
        str, typing.Dict[str, typing.Any]
    ],
    typing.List[
        typing.Tuple[str, typing.Dict[str, typing.Any]]
    ]
]

class ModelInstaller(object):
    __slots__ = ("models",)

    def __init__(self, models: ModelsType) -> None:
        self.models = models

    def install(self):
        results = []
        for model in self.models:
            results.append(snapshot_download(model[0], **model[1]))
        return results


ms = [
    (
        "Qwen/Qwen3-VL-8B-Instruct",
        {
            "local_dir": "/home/ckr-ubuntu/桌面/MyProject/CerebraX/src/cerebrax/utils/D"
        }
    )
]

mi = ModelInstaller(ms)

rs = mi.install()
print(rs)
