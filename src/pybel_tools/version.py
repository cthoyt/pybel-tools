# -*- coding: utf-8 -*-

"""Version information for PyBEL-Tools."""

__all__ = [
    'VERSION',
    'get_version',
]

VERSION = '0.9.1'


def get_version() -> str:
    """Get the current PyBEL Tools version."""
    return VERSION
