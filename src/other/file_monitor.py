"""
构建灵活的文件监控插件系统
"""
from watchdog.observers import Observer, ObserverType
from watchdog import events
from pydantic import BaseModel, field_validator, ValidationError
import typing, types, inspect, uuid

# watchdog.events 模块内部自带的Handler
DefaultHandlers = [i for i in dir(events) if not i.startswith("_") and i.endswith("Handler")]
DefaultCallback = [i for i in dir(getattr(events, DefaultHandlers[0])) if not i.startswith("_")]

ParameterTypes = [
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.KEYWORD_ONLY,
    inspect.Parameter.VAR_KEYWORD,
]

class BuildArguments(BaseModel):
    name: str = "Handler"
    base_class: str = DefaultHandlers[0]
    attr: typing.Optional[typing.Dict[str, typing.Any]] = None

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value:str) -> str:
        if value == "MyHandler":
            raise ValidationError(f"name not is {value}")
        return value

    @field_validator("base_class", mode="before")
    @classmethod
    def validate_base_class(cls, value: str) -> str:
        if value not in DefaultHandlers:
            raise ValidationError(f"Must in {DefaultHandlers}")
        return value

    @field_validator("attr", mode="before")
    @classmethod
    def validate_attr(cls, value: typing.Optional[typing.Dict[str, typing.Any]]) -> typing.Dict[str, typing.Any]:
        if value is None:
            return {}
        for k, v in value.items():
            if isinstance(v, typing.Callable):
                if k in DefaultCallback:
                    if not inspect.isfunction(v) or inspect.iscoroutinefunction(v):
                        raise ValidationError("The callback method must be a regular function")
                    params_iter = iter(inspect.signature(v).parameters.values())
                    try:
                        if next(params_iter).kind in {ParameterTypes[0], ParameterTypes[-2]}:
                            raise ValidationError(f"The first parameter in the {k} function is passed in incorrectly")
                        if next(params_iter).kind in {ParameterTypes[0], ParameterTypes[-2]}:
                            raise ValidationError(f"The first parameter in the {k} function is passed in incorrectly")
                    except StopIteration:
                        raise ValidationError(f"The {k} function lacks necessary formal parameters")
        return value


class FileMonitoringHandler(object):
    def __init__(self) -> None:
        self._handlers = {}
        self._observers = {}

    def get_handlers(self) -> typing.Dict[str, type[typing.Any]]:
        return self._handlers

    def get_observers(self) -> typing.Dict[str, ObserverType]:
        return self._observers

    def new_observer(self, name: str) -> ObserverType:
        new_observer = Observer()
        self._observers[name] = new_observer
        return new_observer

    def build_handler(self,
              name: str = "Handler",
              base_class: str = DefaultHandlers[0],
              attr: typing.Optional[typing.Dict[str, typing.Any]] = None,
              ) -> type[typing.Any]:
        """
        attr里面可以是规定的回调函数也可以是依赖的相关函数和属性
        :param name:
        :param base_class:
        :param attr:
        :return:
        """
        build_args = BuildArguments(
            name=name,
            base_class=base_class,
            attr=attr
        )
        built_class = type(
            build_args.name,
            (getattr(events, build_args.base_class),),
            build_args.attr,
        )
        self._handlers[build_args.name] = built_class
        return built_class


__all__ = [
    "FileMonitoringHandler",
]


