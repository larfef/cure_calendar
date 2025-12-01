"""
Centralized type aliases for the templates_app.

Simple type aliases (ints, Literals) live here.
Complex TypedDicts remain in their domain-specific files.
"""

from typing import Literal

# === Primitive Aliases ===
# These give semantic meaning to basic types

MonthIndex = int
"""0-based month index in the calendar"""

WeekIndex = int
"""0-3, week position within a month"""

ProductId = int
"""Database ID of a Product"""

DayIndex = int
"""0-6, day position within a week (Monday=0)"""


# === Literal Types ===
# Constrained string unions for type safety

TimeSlot = Literal["morning", "evening", "mixed"]
"""When during the day an intake occurs"""


# === Composite Map Types ===
# These define the ContentMap structure used by collector/materializer

# Note: Using string forward reference to avoid circular import
ProductWeekMap = dict[WeekIndex, "list | None"]
"""Maps week index → content for a single product"""

TimeSlotProductMap = dict[ProductId, ProductWeekMap]
"""Maps product ID → week map for a time slot"""

MonthContentMap = dict[TimeSlot, TimeSlotProductMap]
"""Maps time slot → product map for a month"""

ContentMap = dict[MonthIndex, MonthContentMap]
"""Full content structure: month → slot → product → week → content"""
