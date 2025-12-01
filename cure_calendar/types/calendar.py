from typing import TypedDict
from cure_calendar.types.aliases import TimeSlot


class WeekDisplayOptions(TypedDict):
    """Controls visual rendering of the week table"""

    time_column: bool  # Show time labels in first column
    table_header: bool  # Show header row (days of week)


class TimeSlotContent(TypedDict):
    """Content for a specific time period (morning/evening/mixed) within a week"""

    enabled: bool  # Whether this time slot has any scheduled items
    rows: list  # List of TableRowContent dicts (medication schedules)


class WeekSchedule(TypedDict):
    """All time slots for a single week"""

    morning: TimeSlotContent
    evening: TimeSlotContent
    mixed: TimeSlotContent  # Both morning and evening intake
    display: WeekDisplayOptions


class NumLine(TypedDict):
    """Number of rows needed for each time slot"""

    morning: int
    evening: int
    mixed: int


class MonthSummary(TypedDict):
    """Month data with weeks and consolidated line counts"""

    weeks: list[WeekSchedule]
    num_lines: NumLine  # All line counts in one object


# Optional: if you need to represent the full week with metadata
class CalendarWeekRange(TypedDict):
    """Week definition with time range"""

    day_time: TimeSlot  # Which time slot this represents
    start_day: int  # Starting day index
    end_day: int  # Ending day index
    schedule: WeekSchedule
