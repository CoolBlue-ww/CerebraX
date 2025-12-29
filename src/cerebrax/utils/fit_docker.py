from src.cerebrax.common_depend import (
    typing,
    docker,
    ImageNotFound,
    DockerException,
    APIError,
    requests,
    NotFound
)
from src.cerebrax._types import (
DockerImageList,
DefaultContainerQuery,
ContainerRunArgs,
)

# image reference 镜像引用
class DockerImages(object):
    def __init__(self, client: docker.DockerClient) -> None:
        self.client = client

    def pull(self, repository: str, tag : str):
        try:
            image = self.client.images.get(f"{repository}:{tag}")
            return image
        except ImageNotFound:
            try:
                image = self.client.images.pull(repository=repository, tag=tag)
                return image
            except ImageNotFound:
                print("镜像名字错误！")
            except APIError:
                print("仓库错误！")
            except DockerException:
                print("Docker有误！")
            except requests.ReadTimeout:
                print("读取超时！")

    def remove(self, image_reference: str):
        try:
            self.client.images.remove(image_reference=image_reference, force=True)
        except ImageNotFound:
            pass

    def get(self, image_reference: str):
        try:
            image = self.client.images.get(image_reference)
            return image
        except ImageNotFound:
            return None

    def list(self, return_images: bool = False) -> DockerImageList:
        images = self.client.images.list()
        image_references = sorted(
            [tag for image in images for tag in image.tags],
            key=lambda tag: tag.lower()
        )
        if return_images:
            return {
                "images": images,
                "image_references": image_references,
            }
        else:
            return image_references


class DockerContainer(object):
    def __init__(self, client: docker.DockerClient) -> None:
        self.client = client
        self.container = None

    def start(self, query: str = DefaultContainerQuery, args: ContainerRunArgs = None):
        container = None
        _args = args if isinstance(args, typing.Dict) else {}
        try:
            container = self.client.containers.get(query)
        except NotFound:
            pass
        if container:
            if container.status != "running":
                container.start()
        else:
            container = self.client.containers.run(**_args)
        self.container = container

    def stop(self, rm: bool = False):
        if self.container:
            self.container.reload()
            if self.container.status == "running":
                self.container.stop()
                if rm:
                    self.container.remove(v=True)
                self.container = None

    def pause(self):
        if self.container:
            self.container.reload()
            if self.container.status == "running":
                self.container.pause()

    def unpause(self):
        if self.container:
            self.container.reload()
            if self.container.status == "paused":
                self.container.unpause()

    def restart(self):
        if self.container:
            self.container.restart()


from src.cerebrax.internal import docker_client


dc = DockerContainer(docker_client)

args = {
    "image": "hello-world:latest"
}

dc.start(query="hello-world", args=args)
print(dc.container)


