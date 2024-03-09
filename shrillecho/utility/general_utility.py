import json
from typing import Type, TypeVar, Callable, Any

T = TypeVar('T')


def sp_fetch(api_function: Callable, dataclass_type: Type[T], *args, **kwargs) -> T:
    api_response = api_function(*args, **kwargs)
    json_data = json.dumps(api_response)
    return dataclass_type.from_json(json_data)