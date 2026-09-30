import json
import requests
from datetime import datetime, timezone

# Forex Factory weekly economic calendar
API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

# العملات التي نحتاجها للفوركس والذهب
CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "NZD"
}

IMPACTS = {
    "High",
    "Medium",
    "Low"
}


def get_news():
    try:
        response = requests.get(
            API_URL,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            print("ERROR: Unexpected API response")
            return []

        return data

    except Exception as e:
        print("ERROR:", e)
        return []


def clean_event(event):

    currency = str(
        event.get("country", event.get("currency", ""))
    ).upper().strip()

    impact = str(
        event.get("impact", "")
    ).title().strip()

    if currency not in CURRENCIES:
        return None

    if impact not in IMPACTS:
        return None

    return {
        "id": event.get("id"),
        "date": event.get("date"),
        "time": event.get("time"),
        "datetime": event.get("date"),

        "currency": currency,

        "impact": impact,

        "title": event.get(
            "title",
            event.get("event", "")
        ),

        "actual": event.get(
            "actual",
            ""
        ),

        "forecast": event.get(
            "forecast",
            ""
        ),

        "previous": event.get(
            "previous",
            ""
        )
    }


def main():

    print("Downloading economic calendar...")

    events = get_news()

    result = []

    for event in events:

        cleaned = clean_event(event)

        if cleaned is not None:
            result.append(cleaned)

    output = {
        "source": "ForexFactory",
        "updated": datetime.now(
            timezone.utc
        ).isoformat(),

        "count": len(result),

        "events": result
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

    print(
        "Events saved:",
        len(result)
    )


if __name__ == "__main__":
    main()
