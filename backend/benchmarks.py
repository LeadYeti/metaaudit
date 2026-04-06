"""Industry benchmark data for Meta ads performance.

Benchmarks are median values by industry vertical.
Sources: WordStream, Databox, and Revealbot aggregate reports (2024-2025).
All monetary values in USD.
"""

BENCHMARKS = {
    "home_services": {"cpm": 25.0, "cpc": 1.50, "ctr": 1.8, "cpa": 20.0, "frequency_cap": 3.0},
    "real_estate": {"cpm": 20.0, "cpc": 1.80, "ctr": 1.5, "cpa": 25.0, "frequency_cap": 3.0},
    "healthcare": {"cpm": 18.0, "cpc": 1.30, "ctr": 1.6, "cpa": 30.0, "frequency_cap": 3.0},
    "legal": {"cpm": 22.0, "cpc": 2.00, "ctr": 1.4, "cpa": 40.0, "frequency_cap": 3.0},
    "fitness": {"cpm": 15.0, "cpc": 1.00, "ctr": 2.0, "cpa": 15.0, "frequency_cap": 3.0},
    "restaurant": {"cpm": 12.0, "cpc": 0.80, "ctr": 2.5, "cpa": 12.0, "frequency_cap": 3.0},
    "automotive": {"cpm": 20.0, "cpc": 1.60, "ctr": 1.6, "cpa": 25.0, "frequency_cap": 3.0},
    "ecommerce": {"cpm": 14.0, "cpc": 1.10, "ctr": 1.3, "cpa": 18.0, "frequency_cap": 3.0},
    "education": {"cpm": 16.0, "cpc": 1.20, "ctr": 1.7, "cpa": 22.0, "frequency_cap": 3.0},
    "default": {"cpm": 18.0, "cpc": 1.40, "ctr": 1.7, "cpa": 22.0, "frequency_cap": 3.0},
}


def get_benchmarks(industry: str = "default") -> dict:
    """Return benchmark values for the given industry, falling back to default."""
    return BENCHMARKS.get(industry, BENCHMARKS["default"])
