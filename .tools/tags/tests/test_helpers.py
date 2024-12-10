#!/usr/bin/env python3

from typing import Any, Callable
from functools import wraps


def detailed_assert(
    test_name: str,
    input_value: Any,
    expected: Any,
    actual: Any,
    **extra_info: Any
) -> None:
    """
    Assert with detailed failure reporting.
    """
    if actual != expected:
        error_msg = [
            f"\nTest failed: {test_name}",
            f"Input: {input_value!r}",
            f"Expected: {expected!r}",
            f"Got: {actual!r}",
            f"Type of actual result: {type(actual)}",
        ]

        for key, value in extra_info.items():
            error_msg.append(f"{key}: {value!r}")

        raise AssertionError("\n".join(error_msg))


def with_context(
    func: Callable[[Any], Any] | None = None,
    *,
    show_args: bool = True
) -> Callable:
    """
    Decorator to add detailed failure reporting to test functions.
    """
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            try:
                return test_func(*args, **kwargs)
            except AssertionError as e:
                error_msg = [f"\nTest failed: {test_func.__name__}"]
                if show_args and (args or kwargs):
                    if args:
                        error_msg.append(f"Args: {args!r}")
                    if kwargs:
                        error_msg.append(f"Kwargs: {kwargs!r}")
                error_msg.append(str(e))
                raise AssertionError("\n".join(error_msg))
        return wrapper
    return decorator if func is None else decorator(func)
