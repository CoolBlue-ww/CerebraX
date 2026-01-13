import inspect, typing, types
from src.cerebrax.utils import module_loader


class AddonInstanceCreator(object):
    def __init__(self,
                 load_path: str,
                 container_name: str = "Container",
                 ) -> None:
        self.load_path = load_path
        self.container_name = container_name
        self.container = type(container_name, (object,), {})
        self._addon_instances = {}

    @property
    def addon_instances(self) -> typing.Dict:
        return self._addon_instances

    @staticmethod
    def _is_local_sync_obj(name: str, obj: typing.Callable, module: types.ModuleType) -> typing.Tuple[bool, str]:
        if getattr(obj, "__module__", None) == module.__name__:
            if inspect.isfunction(obj) and not inspect.iscoroutinefunction(obj):
                if not name.startswith("_"):
                    return True, "function"
            if inspect.isclass(obj):
                return True, "class"
        return False, "unknow"

    def _sync_process_attrs(self) -> typing.Tuple[typing.Dict, typing.Dict]:
        addons_module = module_loader.sync_load_module(load_path=self.load_path)
        attrs = addons_module.__dict__
        functions, classes = {}, {}
        for name, obj in attrs.items():
            in_module, object_type = self._is_local_sync_obj(name, obj, addons_module)
            if in_module:
                if object_type == "function":
                    functions[name] = obj
                if object_type == "class":
                    classes[name] = obj
        return functions, classes

    async def _async_process_attrs(self) -> typing.Tuple[typing.Dict, typing.Dict]:
        addons_module = await module_loader.async_load_module(load_path=self.load_path)
        attrs = addons_module.__dict__
        functions, classes = {}, {}
        for name, obj in attrs.items():
            in_module, object_type = self._is_local_sync_obj(name, obj, addons_module)
            if in_module:
                if object_type == "function":
                    functions[name] = obj
                if object_type == "class":
                    classes[name] = obj
        return functions, classes

    def sync_create_addons_instances(self) -> typing.Dict:
        functions, classes = self._sync_process_attrs()
        if functions:
            for name, function in functions.items():
                setattr(self.container, name, function)
        self._addon_instances[self.container_name] = self.container()
        if classes:
            for name, class_ in classes.items():
                self._addon_instances[name] = class_()
        return self.addon_instances

    async def async_create_addons_instances(self) -> typing.Dict:
        functions, classes = await self._async_process_attrs()
        if functions:
            for name, function in functions.items():
                setattr(self.container, name, function)
        self._addon_instances[self.container_name] = self.container()
        if classes:
            for name, class_ in classes.items():
                self._addon_instances[name] = class_()
        return self.addon_instances

__all__ = [
    "AddonInstanceCreator",
]
