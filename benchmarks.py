# Industry benchmarks derived from 773K record analysis (excluding Abstrakt)
# Each industry has baseline percentages for contact quality and list tags
# Accounts are scored relative to their industry's benchmarks

INDUSTRY_BENCHMARKS = {
    "Audio Visual": {
        "first_name_pct": 73, "bad_last_name_pct": 30, "title_pct": 73,
        "direct_phone_pct": 38, "mobile_pct": 35, "both_phones_pct": 17,
        "email_pct": 67, "tags_filled_pct": 37, "tier1_pct": 6, "suspension_pct": 29,
    },
    "Commercial Cleaning": {
        "first_name_pct": 85, "bad_last_name_pct": 20, "title_pct": 86,
        "direct_phone_pct": 45, "mobile_pct": 41, "both_phones_pct": 24,
        "email_pct": 77, "tags_filled_pct": 56, "tier1_pct": 25, "suspension_pct": 34,
    },
    "Commercial Electric": {
        "first_name_pct": 90, "bad_last_name_pct": 14, "title_pct": 90,
        "direct_phone_pct": 51, "mobile_pct": 57, "both_phones_pct": 35,
        "email_pct": 84, "tags_filled_pct": 71, "tier1_pct": 26, "suspension_pct": 20,
    },
    "Commercial Fire Protection": {
        "first_name_pct": 94, "bad_last_name_pct": 10, "title_pct": 94,
        "direct_phone_pct": 55, "mobile_pct": 52, "both_phones_pct": 33,
        "email_pct": 87, "tags_filled_pct": 67, "tier1_pct": 32, "suspension_pct": 24,
    },
    "Commercial Flooring": {
        "first_name_pct": 91, "bad_last_name_pct": 11, "title_pct": 91,
        "direct_phone_pct": 55, "mobile_pct": 50, "both_phones_pct": 32,
        "email_pct": 88, "tags_filled_pct": 79, "tier1_pct": 36, "suspension_pct": 25,
    },
    "Commercial Roofing": {
        "first_name_pct": 84, "bad_last_name_pct": 22, "title_pct": 84,
        "direct_phone_pct": 43, "mobile_pct": 38, "both_phones_pct": 23,
        "email_pct": 73, "tags_filled_pct": 44, "tier1_pct": 14, "suspension_pct": 47,
    },
    "Concrete/Asphalt Services": {
        "first_name_pct": 82, "bad_last_name_pct": 21, "title_pct": 83,
        "direct_phone_pct": 44, "mobile_pct": 43, "both_phones_pct": 25,
        "email_pct": 73, "tags_filled_pct": 54, "tier1_pct": 21, "suspension_pct": 28,
    },
    "Construction": {
        "first_name_pct": 88, "bad_last_name_pct": 16, "title_pct": 89,
        "direct_phone_pct": 46, "mobile_pct": 44, "both_phones_pct": 26,
        "email_pct": 79, "tags_filled_pct": 54, "tier1_pct": 19, "suspension_pct": 34,
    },
    "Copy/Print": {
        "first_name_pct": 71, "bad_last_name_pct": 31, "title_pct": 71,
        "direct_phone_pct": 32, "mobile_pct": 37, "both_phones_pct": 17,
        "email_pct": 61, "tags_filled_pct": 30, "tier1_pct": 13, "suspension_pct": 26,
    },
    "EV Charging Stations": {
        "first_name_pct": 64, "bad_last_name_pct": 38, "title_pct": 60,
        "direct_phone_pct": 35, "mobile_pct": 45, "both_phones_pct": 17,
        "email_pct": 46, "tags_filled_pct": 12, "tier1_pct": 6, "suspension_pct": 17,
    },
    "Elevators": {
        "first_name_pct": 92, "bad_last_name_pct": 13, "title_pct": 93,
        "direct_phone_pct": 45, "mobile_pct": 46, "both_phones_pct": 23,
        "email_pct": 84, "tags_filled_pct": 36, "tier1_pct": 11, "suspension_pct": 52,
    },
    "HVAC": {
        "first_name_pct": 82, "bad_last_name_pct": 21, "title_pct": 82,
        "direct_phone_pct": 42, "mobile_pct": 42, "both_phones_pct": 25,
        "email_pct": 70, "tags_filled_pct": 36, "tier1_pct": 13, "suspension_pct": 35,
    },
    "IT/Cyber Security/MSP": {
        "first_name_pct": 87, "bad_last_name_pct": 16, "title_pct": 87,
        "direct_phone_pct": 44, "mobile_pct": 39, "both_phones_pct": 21,
        "email_pct": 78, "tags_filled_pct": 41, "tier1_pct": 11, "suspension_pct": 37,
    },
    "LED Lighting": {
        "first_name_pct": 95, "bad_last_name_pct": 10, "title_pct": 95,
        "direct_phone_pct": 56, "mobile_pct": 45, "both_phones_pct": 30,
        "email_pct": 86, "tags_filled_pct": 51, "tier1_pct": 20, "suspension_pct": 58,
    },
    "Landscape Services": {
        "first_name_pct": 94, "bad_last_name_pct": 9, "title_pct": 94,
        "direct_phone_pct": 57, "mobile_pct": 50, "both_phones_pct": 33,
        "email_pct": 88, "tags_filled_pct": 79, "tier1_pct": 47, "suspension_pct": 24,
    },
    "Material Handling": {
        "first_name_pct": 64, "bad_last_name_pct": 37, "title_pct": 63,
        "direct_phone_pct": 47, "mobile_pct": 35, "both_phones_pct": 27,
        "email_pct": 63, "tags_filled_pct": 59, "tier1_pct": 49, "suspension_pct": 10,
    },
    "Mortgage - LO Recruitment": {
        "first_name_pct": 100, "bad_last_name_pct": 0, "title_pct": 93,
        "direct_phone_pct": 26, "mobile_pct": 54, "both_phones_pct": 22,
        "email_pct": 97, "tags_filled_pct": 0, "tier1_pct": 0, "suspension_pct": 13,
    },
    "Mortgage - Realtor Referral": {
        "first_name_pct": 100, "bad_last_name_pct": 0, "title_pct": 27,
        "direct_phone_pct": 0, "mobile_pct": 99, "both_phones_pct": 0,
        "email_pct": 100, "tags_filled_pct": 1, "tier1_pct": 0, "suspension_pct": 2,
    },
    "Other": {
        "first_name_pct": 92, "bad_last_name_pct": 13, "title_pct": 92,
        "direct_phone_pct": 50, "mobile_pct": 35, "both_phones_pct": 19,
        "email_pct": 81, "tags_filled_pct": 37, "tier1_pct": 16, "suspension_pct": 65,
    },
    "Other (Non-Local)": {
        "first_name_pct": 88, "bad_last_name_pct": 14, "title_pct": 87,
        "direct_phone_pct": 42, "mobile_pct": 46, "both_phones_pct": 25,
        "email_pct": 74, "tags_filled_pct": 38, "tier1_pct": 13, "suspension_pct": 27,
    },
    "Painting": {
        "first_name_pct": 85, "bad_last_name_pct": 19, "title_pct": 86,
        "direct_phone_pct": 46, "mobile_pct": 45, "both_phones_pct": 26,
        "email_pct": 77, "tags_filled_pct": 50, "tier1_pct": 17, "suspension_pct": 31,
    },
    "Physical Security": {
        "first_name_pct": 89, "bad_last_name_pct": 14, "title_pct": 89,
        "direct_phone_pct": 45, "mobile_pct": 47, "both_phones_pct": 26,
        "email_pct": 81, "tags_filled_pct": 58, "tier1_pct": 25, "suspension_pct": 31,
    },
    "Power Washing": {
        "first_name_pct": 98, "bad_last_name_pct": 8, "title_pct": 99,
        "direct_phone_pct": 59, "mobile_pct": 46, "both_phones_pct": 31,
        "email_pct": 86, "tags_filled_pct": 60, "tier1_pct": 22, "suspension_pct": 24,
    },
    "Solar": {
        "first_name_pct": 92, "bad_last_name_pct": 12, "title_pct": 92,
        "direct_phone_pct": 55, "mobile_pct": 52, "both_phones_pct": 34,
        "email_pct": 86, "tags_filled_pct": 65, "tier1_pct": 30, "suspension_pct": 39,
    },
}

# List Tag code to tier mapping
LIST_TAG_TIERS = {
    "A": 1,
    "T": 1,
    "W": 2,
    "NI": 2,
    "I1": 3,
    # Numeric tier values (transition in progress)
    "1": 1,
    "2": 2,
    "3": 3,
}
# NR, I, I2, I3, blank = untiered (no points)
