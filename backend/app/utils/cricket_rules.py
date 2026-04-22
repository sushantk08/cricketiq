FORMAT_RULES = {
    "T20": {
        "max_overs": 20,
        "max_balls": 120,
        "phase_boundaries": {
            "powerplay": (0, 6),
            "middle": (6, 15),
            "death": (15, 20),
        },
    },
    "ODI": {
        "max_overs": 50,
        "max_balls": 300,
        "phase_boundaries": {
            "powerplay": (0, 10),
            "middle": (10, 40),
            "death": (40, 50),
        },
    },
}


def get_format_rules(match_type: str) -> dict:
    return FORMAT_RULES.get(
        match_type.upper(),
        FORMAT_RULES["T20"],
    )