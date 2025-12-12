import typing, fastapi

def get_implementation_classes(request: fastapi.Request) -> typing.Any:
    implementation_classes = request.app.state.implementation_classes
    return implementation_classes

def get_shared_instances(request: fastapi.Request) -> typing.Any:
    shared_instance = request.app.state.shared_instances
    return shared_instance

