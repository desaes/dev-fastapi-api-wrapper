from typing import List, Dict, Tuple, Union, Any, NoReturn, Mapping, Literal
from functools import reduce

def deep_get(dictionary: dict, keys: str, default=None) -> Any:
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)

def json_mapper(data: Union[dict, list], **kwargs) -> list:
    if kwargs.get('map_keys') and kwargs.get('map_values'):
        ok = kwargs['map_keys'].replace(' ','').split(',')
        if isinstance(data, dict):
            if data.get('content'):
                data = data['content']
            else:
                data = [data]
        _data = []
        for element in data:
            md = {}
            i = 0
            for item in kwargs['map_values'].replace(' ','').split(','):
                value = deep_get(element, item)
                if value:
                    md[ok[i]] = str(value)
                    i += 1
            _data.append(md)
        return _data
    else:
        return data