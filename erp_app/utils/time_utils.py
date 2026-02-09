from datetime import datetime, timedelta, timezone

def get_ist():
    """Returns the current Indian Standard Time (IST) as a timezone-aware datetime object."""
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def get_ist_date():
    """Returns the current date in Indian Standard Time (IST)."""
    return get_ist().date()
