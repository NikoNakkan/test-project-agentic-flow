"""In-memory Hello World click counter (resets on server restart)."""

_count: int = 0


def get_count() -> int:
    return _count


def increment() -> int:
    global _count
    _count += 1
    return _count


def reset_count() -> None:
    """Reset counter — for tests only."""
    global _count
    _count = 0
