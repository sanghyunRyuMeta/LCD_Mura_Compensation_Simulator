"""
Utilities for reading and writing tab-separated config files (reg.txt, lxs_para_sim).
"""

import os
import re


def read_config(filepath: str) -> dict[str, str]:
    """Read a tab/space-separated key-value config file into a dict."""
    config = {}
    if not os.path.isfile(filepath):
        return config
    with open(filepath, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                config[parts[0]] = parts[1]
    return config


def write_config_value(filepath: str, key: str, value: str) -> bool:
    """Update a single key's value in a tab-separated config file. Returns True if found & updated."""
    if not os.path.isfile(filepath):
        return False

    with open(filepath, "r") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        # Skip empty lines to prevent parsing errors
        stripped = line.strip()
        if not stripped:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0] == key:
            # Preserve the original whitespace style (tabs)
            new_line = re.sub(
                r'^(' + re.escape(key) + r'\s+)\S+',
                r'\g<1>' + value,
                line,
            )
            new_lines.append(new_line.rstrip() + '\n')
            found = True
        else:
            new_lines.append(line.rstrip() + '\n')

    if found:
        with open(filepath, "w") as f:
            f.writelines(new_lines)
    return found


def write_config_values(filepath: str, updates: dict[str, str]) -> list[str]:
    """Update multiple keys in a config file. Returns list of keys that were updated."""
    if not os.path.isfile(filepath):
        return []

    with open(filepath, "r") as f:
        lines = f.readlines()

    updated_keys = []
    new_lines = []
    for line in lines:
        # Skip empty lines to prevent parsing errors
        stripped = line.strip()
        if not stripped:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0] in updates:
            new_line = re.sub(
                r'^(' + re.escape(parts[0]) + r'\s+)\S+',
                r'\g<1>' + updates[parts[0]],
                line,
            )
            new_lines.append(new_line.rstrip() + '\n')
            updated_keys.append(parts[0])
        else:
            new_lines.append(line.rstrip() + '\n')

    if updated_keys:
        with open(filepath, "w") as f:
            f.writelines(new_lines)
    return updated_keys
