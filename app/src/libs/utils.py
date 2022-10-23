from typing import List, Dict, Tuple, Union, Any, NoReturn, Mapping, Literal

def print_nothing(var: Union[str, int]) -> Union[str, int]:
    if var == '0':
        return '0'
    elif var == 0:
        return 0
    elif var:
        return var
    return ''