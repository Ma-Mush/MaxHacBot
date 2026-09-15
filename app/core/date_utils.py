"""Date utility functions for report time windows and period comparisons."""
from datetime import datetime, time, timedelta, timezone
from typing import Tuple


def get_utc_now() -> datetime:
    """Current UTC datetime."""
    return datetime.now(timezone.utc)


def parse_date_range(
    range_name: str = "last_7_days",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Tuple[datetime, datetime]:
    """Resolve named date ranges into start and end UTC datetimes.
    
    Supported:
    - today
    - yesterday
    - last_7_days
    - last_30_days
    - this_month
    - custom
    """
    now = get_utc_now()
    today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    today_end = now

    norm = range_name.lower().strip() if range_name else "last_7_days"

    if norm == "today":
        return today_start, today_end

    elif norm == "yesterday":
        y_start = today_start - timedelta(days=1)
        y_end = datetime.combine(y_start.date(), time.max, tzinfo=timezone.utc)
        return y_start, y_end

    elif norm == "last_7_days":
        return now - timedelta(days=7), now

    elif norm == "last_30_days":
        return now - timedelta(days=30), now

    elif norm == "this_month":
        month_start = today_start.replace(day=1)
        return month_start, now

    elif norm == "custom":
        if start_date and end_date:
            s = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
            e = end_date if end_date.tzinfo else end_date.replace(tzinfo=timezone.utc)
            return s, e
        elif start_date:
            s = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
            return s, now
        return now - timedelta(days=7), now

    # Default fallback
    return now - timedelta(days=7), now


def get_previous_period(start_date: datetime, end_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate the equivalent prior period for comparative analytics."""
    duration = end_date - start_date
    prior_end = start_date
    prior_start = prior_end - duration
    return prior_start, prior_end
