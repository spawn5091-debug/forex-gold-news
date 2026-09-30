import json
import requests
from datetime import datetime, timezone

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

CURRENCIES = [
    "USD", "EUR", "GBP", "JPY",
    "CHF", "CAD", "AUD", "NZD"
]

IMPACTS = ["High", "Medium", "Low"]


def to_number(value):
    if value is None:
        return None

    s = str(value).strip()
    s = s.replace(",", "")
    s = s.replace("%", "")
    s = s.replace("$", "")

    if s in ["", "-", "—", "N/A"]:
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


def get_direction(actual, forecast):
    a = to_number(actual)
    f = to_number(forecast)

    if a is None or f is None:
        return "Unknown"

    if a > f:
        return "Higher"

    if a < f:
        return "Lower"

    return "Neutral"


def get_indicator_direction(title):
    t = title.lower()

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


def get_strength(direction, indicator):
    if direction == "Unknown":
        return "Unknown"

    if indicator == "Neutral":
        return "Neutral"

    if indicator == "Higher":
        if direction == "Higher":
            return "Stronger"
        if direction == "Lower":
            return "Weaker"

    if indicator == "Lower":
        if direction == "Lower":
            return "Stronger"
        if direction == "Higher":
            return "Weaker"

    return "Unknown"


def main():

    print("Downloading economic calendar...")

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    data = response.json()

    events = []

    for item in data:

        currency = str(
            item.get(
                "country",
                item.get("currency", "")
            )
        ).upper().strip()

        if currency not in CURRENCIES:
            continue

        impact = str(
            item.get("impact", "")
        ).title().strip()

        if impact not in IMPACTS:
            continue

        title = str(
            item.get(
                "title",
                item.get("event", "")
            )
        ).strip()

        actual = item.get("actual", "")
        forecast = item.get("forecast", "")
        previous = item.get("previous", "")

        direction = get_direction(
            actual,
            forecast
        )

        indicator = get_indicator_direction(
            title
        )

        strength = get_strength(
            direction,
            indicator
        )

        events.append({
            "id": item.get("id"),
            "date": item.get("date", ""),
            "time": item.get("time", ""),
            "datetime": item.get("date", ""),
            "currency": currency,
            "impact": impact,
            "title": title,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "direction": direction,
            "indicator_direction": indicator,
            "strength": strength
        })

    output = {
        "source": "ForexFactory",
        "source_type": "unofficial_feed",
        "updated": datetime.now(
            timezone.utc
        ).isoformat(),
        "count": len(events),
        "events": events
    }

    with open(
        "economic_calendar.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Events saved:", len(events))
    print("Economic calendar updated successfully.")


if __name__ == "__main__":
    main()
