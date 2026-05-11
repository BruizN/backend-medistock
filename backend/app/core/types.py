from typing import Annotated

from pydantic import AfterValidator


def clean_text(v: str) -> str:
    """Removes leading and trailing whitespaces."""
    if isinstance(v, str):
        return v.strip()
    return v


def clean_code(v: str) -> str:
    """Removes leading and trailing whitespaces and converts to uppercase."""
    if isinstance(v, str):
        return v.strip().upper()
    return v


CleanText = Annotated[str, AfterValidator(clean_text)]
CleanCode = Annotated[str, AfterValidator(clean_code)]
