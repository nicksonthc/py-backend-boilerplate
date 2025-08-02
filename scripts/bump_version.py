#!/usr/bin/env python3
"""
Version bumping script for Python Backend.

Usage:
    python scripts/bump_version.py major|minor|patch

This script updates the version number in src/version.py according to
semantic versioning principles:
- major: Breaking changes - increment major version, reset minor & patch
- minor: New features (backward compatible) - increment minor version, reset patch
- patch: Bug fixes (backward compatible) - increment patch version
"""

import os
import re
import sys


VERSION_FILE_PATH = os.path.join("version.py")


def read_version():
    """Read the current version from the version file."""
    with open(VERSION_FILE_PATH, "r") as f:
        content = f.read()
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        raise ValueError("Could not find version string in version.py")


def bump_version(version_type):
    """Bump the version according to semantic versioning."""
    current = read_version()
    major, minor, patch = map(int, current.split("."))

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        raise ValueError("Version type must be 'major', 'minor', or 'patch'")

    new_version = f"{major}.{minor}.{patch}"
    return new_version


def update_version_file(new_version):
    """Update the version in the version file."""
    with open(VERSION_FILE_PATH, "r") as f:
        content = f.read()

    updated = re.sub(r'__version__ = ["\']([^"\']+)["\']', f'__version__ = "{new_version}"', content)

    with open(VERSION_FILE_PATH, "w") as f:
        f.write(updated)


def main():
    """Main function to run the script."""
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    version_type = sys.argv[1]
    try:
        current = read_version()
        new_version = bump_version(version_type)
        update_version_file(new_version)
        print(f"Version bumped from {current} to {new_version}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
