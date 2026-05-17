from __future__ import annotations

from configparser import ConfigParser


def load_config(filename: str = "database.ini", section: str = "postgresql") -> dict[str, str]:
    """Load DB connection parameters from an INI file.

    Expected keys in [postgresql]:
      host, port, dbname, user, password
    """
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise RuntimeError(f"Section [{section}] not found in {filename}")

    return {k: v for k, v in parser.items(section)}
