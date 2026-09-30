import json
import requests
from datetime import datetime, timezone

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]


def number(value):
    if value is None:
        return None

    s = str(value).strip().replace(",", "").replace("%", "")

    if s in ("", "-", "—", "N/A"):
        return None

    multiplier = 1

    if s.upper().endswith("K"):
        multiplier = 1000
        s = s[:-1]
    elif s.upper().endswith("M"):
        multiplier = 1000000
        s = s[:-1]
    elif s.upper().endswith("B"):
        multiplier = 1000000000
        s = s[:-1]

    try:
        return float(s) * multiplier
    except:
        return None


def direction(actual, forecast):
    a = number(actual)
    f = number(forecast)

    if a is None or f is None:
        return "Unknown"

    if a > f:
        return "Higher"

    if a < f:
        return "Lower"

    return "Neutral"


def indicator_direction(title):
    t = title.lower()

    # Lower = Stronger
    if any(x in t for x in [
        "unemployment claims",
        "jobless claims",
        "initial claims",
        "continuing claims",
        "unemployment rate",
        "unemployment",
        "jobless"
    ]):
        return "Lower"

    # Higher = Stronger
    if any(x in t for x in [
        "non-farm",
        "nonfarm",
        "nfp",
        "employment",
        "retail sales",
        "gdp",
        "industrial production",
        "pmi",
        "consumer confidence",
        "consumer sentiment",
        "durable goods",
        "hourly earnings",
        "wages"
    ]):
        return "Higher"

    return "Neutral"


def strength(actual_direction, ind_direction):

    if actual_direction == "Unknown":
        return "Unknown"

    if ind_direction == "Neutral":
        return "Neutral"

    if ind_direction == "Higher":
        if actual_direction == "Higher":
            return "Stronger"
        if actual_direction == "Lower":
            return "Weaker"

    if ind_direction == "Lower":
        if actual_direction == "Lower":
            return "Stronger"
        if actual_direction == "Higher":
            return "Weaker"

    return "Unknown"


def main():

    print("Downloading economic calendar...")

    try:
        r = requests.get(
            URL,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        r.raise_for_status()
        data = r.json()

    except Exception as e:
        print("ERROR:", e)
        data = []

    events = []

    for item in data:

        currency = str(
            item.get(
                "
