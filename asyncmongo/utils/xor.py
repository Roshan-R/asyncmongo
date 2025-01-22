
def _xor(fir: bytes, sec: bytes) -> bytes:
    """XOR two byte strings together."""
    return b"".join([bytes([x ^ y]) for x, y in zip(fir, sec)])
