from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation


def parse_str(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    return value.strip()


def parse_int(value: str | None) -> int | None:
    if not value or not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def parse_decimal(value: str | None) -> Decimal | None:
    if not value or not value.strip():
        return None
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return None


def parse_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def parse_limit_offset(args: object) -> tuple[int, int]:
    limit = parse_int(args.get("limit")) or 20
    offset = parse_int(args.get("offset")) or 0
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return limit, offset
