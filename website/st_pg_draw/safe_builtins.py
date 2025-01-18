class UnsafeCodeException(Exception):
    pass


def validate_code(code):
    if "__" in code:
        raise UnsafeCodeException("Access to dunder methods and attributes is not supported.")
    if ".save" in code or ".load" in code:
        raise UnsafeCodeException("Saving/loading is not supported.")
    

safe_builtins = {
    'range': range,
    'list': list,
    'set': set,
    'tuple': tuple,
    'dict': dict,
    'len': len,
    'min': min,
    'max': max,
    'abs': abs,
    'pow': pow,
    'round': round,
    'all': all,
    'any': any,
    'divmod': divmod,
    'hex': hex,
    'sorted': sorted,
    'enumerate': enumerate,
    'zip': zip,
    'map': map,
    'reversed': reversed,
    'filter': filter,
    'int': int,
    'float': float,
    'str': str,
}