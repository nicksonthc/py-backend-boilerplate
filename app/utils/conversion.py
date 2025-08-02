import pytz
from typing import Optional, Tuple
from app.core.config import CONFIG
from datetime import date, datetime, timedelta, timezone


def get_current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


def get_local_dt_iso(utc_dt: datetime | None) -> Optional[datetime]:
    """Convert a naive datetime (assumed to be UTC) to local timezone datetime

    Args:
        utc_dt (datetime): The UTC datetime, either naive or aware.

    Returns:
        datetime: The local timezone datetime.
    """
    if not utc_dt:
        return
    # mssql store naive dt, require localize
    if not utc_dt.tzinfo:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(pytz.timezone(CONFIG.TIME_ZONE)).isoformat()


def get_local_dt_human_readable(utc_dt: datetime) -> Optional[str]:
    """Convert a UTC datetime to local timezone and return as human-readable string

    Args:
        utc_dt (datetime): The UTC datetime, either naive or aware.

    Returns:
        str: Human-readable local datetime string, e.g., '2025-05-30 11:17 AM'
    """
    if not utc_dt:
        return None
    if not utc_dt.tzinfo:
        utc_dt = pytz.utc.localize(utc_dt)
    local_dt = utc_dt.astimezone(pytz.timezone(CONFIG.TIME_ZONE))
    return local_dt.strftime("%Y-%m-%d %I:%M %p")


def get_utc_dt(local_dt: datetime | None) -> datetime:
    """Convert local datetime to UTC datetime

    Args:
        local_dt (datetime): Local datetime (e.g. GMT+8)

    Returns:
        datetime: UTC datetime
    """

    time_zone = pytz.timezone(CONFIG.TIME_ZONE)
    # Handle both naive and timezone-aware datetimes
    if local_dt.tzinfo is None:
        local_dt = time_zone.localize(local_dt)
    return local_dt.astimezone(pytz.UTC)


def get_date_now_iso() -> Tuple[str, str]:
    dt_now = datetime.now(pytz.timezone(CONFIG.TIME_ZONE))
    dt_next = dt_now + timedelta(days=1)

    return dt_now.isoformat(), dt_next.isoformat()


def get_time_zone():
    return pytz.timezone(CONFIG.TIME_ZONE)


def get_today_date() -> date:
    """Get today date in obj in config TIMEZONE"""
    time_zone = get_time_zone()
    current_time = datetime.now(time_zone)
    return current_time.date()


def get_today_date_str() -> str:
    """Get todat date in string in config TIMEZONE"""
    time_zone = get_time_zone()
    current_time = datetime.now(time_zone)
    date_string = current_time.strftime("%Y-%m-%d")
    return date_string


def get_today_utc_start_end_time() -> Tuple[datetime, datetime]:
    """Get earliest and latest datetime of today in config TIMEZONE"""
    time_zone = get_time_zone()
    current_time = datetime.now(time_zone)
    today_date = current_time.date()
    utc_start = time_zone.localize(datetime.combine(today_date, datetime.min.time())).astimezone(pytz.utc)
    utc_end = time_zone.localize(datetime.combine(today_date, datetime.max.time())).astimezone(pytz.utc)

    return utc_start, utc_end


def get_date_utc_start_end_time(date) -> Tuple[datetime, datetime]:
    """Get earliest and latest datetime of a date in config TIMEZONE"""
    time_zone = get_time_zone()
    utc_start = time_zone.localize(datetime.combine(date, datetime.min.time())).astimezone(pytz.utc)
    utc_end = time_zone.localize(datetime.combine(date, datetime.max.time())).astimezone(pytz.utc)

    return utc_start, utc_end


def get_range_utc_start_end_time(from_date, to_date) -> Tuple[datetime, datetime]:
    """Get earliest and latest datetime of a date in config TIMEZONE"""
    time_zone = get_time_zone()
    utc_start = time_zone.localize(datetime.combine(from_date, datetime.min.time())).astimezone(pytz.utc)
    utc_end = time_zone.localize(datetime.combine(to_date, datetime.max.time())).astimezone(pytz.utc)

    return utc_start, utc_end


def datetime_console() -> str:
    """Return UTC datetime in console format"""
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC +00")


def get_dt_from_yymmdd(date_str: str) -> date:
    """Convert YYMMDD to date with zeroed time components

    Args:
        date_str (str): format YYMMDD
    """

    dt = datetime.strptime(date_str, "%y%m%d")
    return dt


def convert_utc_to_local_iso(utc_time):
    return utc_time.replace(tzinfo=pytz.utc).astimezone(get_time_zone()).isoformat()
