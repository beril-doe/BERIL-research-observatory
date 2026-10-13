"""Addresses: how the context layer names a resource to its callers.

The backend names resources by URI, and its URIs carry its own scheme and
layout. Callers never see one. An address is the path below the corpus root —
``<owner>/<project>/<path>`` — the same three parts the read routes take as
``owner``, ``project`` and ``path``, so any address a response returns can be
fed back into a read. Central docs follow the same rule under the house
account: ``beril/docs/<doc>/...``.

This module is the one place a backend URI becomes an address. Response models
serialize their URI fields through :func:`to_address`; the routes that pass
backend payloads through (``/ls``, ``/grep``) rewrite them with it.
"""

from typing import Annotated

from pydantic import PlainSerializer

# The corpus root: every user's projects, and the house account's central docs.
USERS_TARGET_URI = "viking://resources/users/"


def to_address(uri: str) -> str:
    """The caller-facing address of a backend URI.

    Idempotent — an address maps to itself — because a response model may be
    serialized, validated and serialized again on its way out. A URI outside
    the corpus is never expected (reads are bounded to it); one that appears
    anyway loses its scheme rather than echoing the backend's name.
    """
    if uri.startswith(USERS_TARGET_URI):
        return uri[len(USERS_TARGET_URI):].strip("/")
    if uri == USERS_TARGET_URI.rstrip("/"):
        return ""
    return uri.split("://", 1)[-1].strip("/")


def _optional_address(uri: str | None) -> str | None:
    return None if uri is None else to_address(uri)


# A backend URI held internally, serialized as an address. JSON only: that is
# how a response leaves BERIL, while a Python-mode dump inside BERIL keeps the
# URI it can still act on.
Address = Annotated[
    str, PlainSerializer(to_address, return_type=str, when_used="json")
]
OptionalAddress = Annotated[
    str | None,
    PlainSerializer(_optional_address, return_type=str | None, when_used="json"),
]
