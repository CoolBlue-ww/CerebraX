from src.cerebrax.common_depend import (
    typing,
    docker,
    ImageNotFound,
    DockerException,
    APIError,
    requests,
)

# image reference 镜像引用
class DockerImage(object):
    def __init__(self, docker_client: docker.DockerClient) -> None:
        self.docker_client = docker_client

    def pull(self, name: str, tag : str):
        try:
            image = self.docker_client.images.get(f"{name}:{tag}")
            return image
        except ImageNotFound:
            try:
                image = self.docker_client.images.pull(name=name, tag=tag)
                return image
            except ImageNotFound:
                print("镜像名字错误！")
            except APIError:
                print("仓库错误！")
            except DockerException:
                print("Docker有误！")
            except requests.ReadTimeout:
                print("读取超时！")

    def get(self, name: str, tag: str):
        try:
            image = self.docker_client.images.get(f"{name}:{tag}")
            return image
        except ImageNotFound:
            return None

    def list(self) -> typing.Tuple:
        images = self.docker_client.images.list()
        image_references = sorted([image.tag for image in images], key=str.lower)
        return image_references, images
