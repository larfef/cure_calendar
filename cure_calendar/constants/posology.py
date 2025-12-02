# ID -> Label

# 1     Labotix CoPlus
# 2     Resvératrol
# 3     Labotix MB
# 4     Magnésium
# 7     L-Tryptophane
# 8     Multi Vitamine B
# 9     Omega 3 Epax®
# 10    EPP
# 11    ADP Biotics
# 13    Mucopure (avec Glutamine)
# 14    NADH+
# 15    Adrenex
# 16    Ashwagandha Bio KSM-66
# 17    ERGY Calme
# 18    Allicine
# 19    Labotix Multifibre
# 20    Berberine
# 23    Resveratrol
# 24    Mo-Zyme
# 25    Permea Intest
# 26    Alfa Energy

MULTIPLE_PRODUCT_UNIT_RULES = {
    "exceptions": [
        3,
        13,
        19,
        25,
    ],
    0: {
        1: {
            "always": [
                11,
                15,
                16,
                17,
            ],
        },
        2: {
            "always": [
                11,
                15,
                16,
                17,
            ],
        },
    },
    1: {
        1: {
            "always": [
                3,
                13,
                15,
                16,
                17,
            ],
        },
        2: {
            "always": [
                15,
                16,
                17,
            ],
        },
    },
}

DELAY_RULES = {
    0: {
        "delay": {
            10: 15,
        }
    },
    1: {
        "delay": {
            10: None,
        }
    },
}

MAX_STARTING_DAYS = 29

# In cure_calendar/constants/posology.py

DAYS_PER_MONTH = 28
"""Standard month duration in days (4 weeks)"""

MONTH_BOUNDARY_ADJUSTMENT_WINDOW = 8
"""Days after month boundary where we round back to previous month end"""

MAX_WEEKS = 12
"""Maximum weeks to display in templates"""
