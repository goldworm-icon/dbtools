from iconservice.base.address import Address


def str_to_int(value: str) -> int:
    if isinstance(value, int):
        return value

    if value.startswith('0x') or value.startswith('-0x'):
        base = 16
    else:
        base = 10

    return int(value, base)


def object_to_str(value) -> str:
    if isinstance(value, Address):
        return str(value)
    elif isinstance(value, int):
        return hex(value)
    elif isinstance(value, bytes):
        return f'0x{value.hex()}'

    return value


def remove_0x_prefix(value):
    if is_0x_prefixed(value):
        return value[2:]
    return value


def is_0x_prefixed(value):
    return value.startswith('0x')


def convert_hex_str_to_bytes(value: str):
    """Converts hex string prefixed with '0x' into bytes."""
    return bytes.fromhex(remove_0x_prefix(value))


def is_str(value):
    str_types = (str,)
    return isinstance(value, str_types)


def convert_hex_str_to_int(value: str):
    """Converts hex string prefixed with '0x' into int."""
    if is_str(value):
        return int(value, 16)
    else:
        return value

