import textwrap
from typing import Any

from .notebook import add_cell_timer


def print_wrapped(
    x: Any,
    width: int=80,
    subsequent_indent: str=" ",
) -> None:
    """
    Wraps `print` and passes the input through `textwrap` to wrap
    at a given column width
    """
    columns_repr = repr(list(x))
    print(textwrap.fill(
        columns_repr,
        width=width,
        subsequent_indent=subsequent_indent,
    ))


__all__ = [
    "add_cell_timer",
    "print_wrapped",
]
