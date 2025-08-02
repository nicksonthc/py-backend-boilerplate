"""
Version information for py-backend.

This module provides the version information for the package.
The version follows the Semantic Versioning scheme (https://semver.org/):
MAJOR.MINOR.PATCH
"""

__version__ = "0.9.2"


def get_version():
    """Return the current version of the package."""
    return __version__


def get_version_parts():
    """Return the version parts as a tuple (major, minor, patch)."""
    parts = __version__.split(".")
    if len(parts) == 3:
        return int(parts[0]), int(parts[1]), int(parts[2])
    return 0, 0, 0


def get_version_info():
    """Return the version information as a dictionary."""
    major, minor, patch = get_version_parts()
    return {"version": __version__, "major": major, "minor": minor, "patch": patch}
