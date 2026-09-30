import json
import requests
from datetime import datetime, timezone

# =========================================================
# Economic Calendar Source
# =========================================================

API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

# العملات المطلوبة للفوركس والذهب
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


# =========================================================
# News Direction
# =========================================================

def get_direction(actual, forecast):
    """
    يحدد اتجاه الخبر حسب:
    Actual > Forecast  = Higher
    Actual < Forecast  = Lower
    """

    if actual in [None, "", "-"] or forecast in [None, "", "-"]:
        return "Unknown"

    try:
        a = float(str(actual).replace(",", ""))
        f = float(str(forecast).replace(",", ""))

        if a > f:
            return "Higher"

        if a < f:
            return "Lower"

        return "Neutral"

    except Exception:
        return "Unknown"


# =========================================================
# Strength
# =========================================================

def get_strength(direction, indicator_direction):
    """
    indicator_direction:
    Higher = Higher value is stronger
    Lower  = Lower value is stronger
    Neutral = no directional interpretation
    """

    if direction == "Unknown":
        return "Unknown"

    if indicator_direction == "Neutral":
        return "Neutral"

    if indicator_direction == "Higher":
        if direction == "Higher":
            return "Stronger"
        elif direction == "Lower":
            return "Weaker"

    if indicator_direction == "Lower":
        if direction == "Lower":
            return "Stronger"
        elif direction == "Higher":
            return "Weaker"

    return "Unknown"


# =========================================================
# Indicator Direction Rules
# =========================================================

def get_indicator_direction(title):

    title = title.lower().strip()

    # انخفاض الرقم = قوة
    lower_is_stronger = [
        "unemployment",
        "unemployment claims",
        "jobless claims",
        "initial claims",
        "continuing claims",
        "unemployment rate",
        "jobless",
        "trade balance",
        "budget balance",
        "government budget"
    ]

    # ارتفاع الرقم = قوة
    higher_is_stronger = [
        "non-farm",
        "nonfarm",
        "nfp",
        "employment change",
        "employment",
        "retail sales",
        "gdp",
        "gross domestic product",
        "industrial production",
        "manufacturing",
        "services pmi",
        "manufacturing pmi",
        "pmi",
        "consumer confidence",
        "consumer sentiment",
        "durable goods",
        "core durable goods",
        "average hourly earnings",
        "wages",
        "cpi",
        "core cpi",
        "inflation",
        "ppi",
        "core ppi"
    ]

    # مؤشرات لا نريد تفسيرها تلقائياً
    neutral = [
        "interest rate decision",
        "cash rate",
        "fomc statement",
        "fomc",
        "ecb",
        "boe",
        "boj",
        "snb",
        "boc",
        "rbnz",
        "rba",
        "fed",
        "central bank"
    ]

    for item in neutral:
        if item in title:
            return "Neutral"

    for item in lower_is_stronger:
        if item in title:
            return "Lower"

    for item in higher_is_stronger:
        if item in title:
            return "Higher"

    return "Neutral"


# =========================================================
# Download Calendar
# =========================================================

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


# =========================================================
# Clean Event
# =========================================================

def clean_event(event):

    currency = str(
        event.get(
            "country",
            event.get(
                "currency",
                ""
            )
        )
    ).upper().strip()

    impact = str(
        event.get(
            "impact",
            ""
        )
    ).title().strip()

    if currency not in CURRENCIES:
        return None

    if impact not in IMPACTS:
        return None

    title = str(
        event.get(
            "title",
            event.get(
                "event",
                ""
            )
        )
    ).strip()

    actual = event.get(
        "actual",
        ""
    )

    forecast = event.get(
        "forecast",
        ""
    )

    previous = event.get(
        "previous",
        ""
    )

    direction = get_direction(
        actual,
        forecast
    )

    indicator_direction = get_indicator_direction(
        title
    )

    strength = get_strength(
        direction,
        indicator_direction
    )

    return {

        "id": event.get("id"),

        "date": event.get(
            "date",
            ""
        ),

        "time": event.get(
            "time",
            ""
        ),

        "datetime": event.get(
            "date",
            ""
        ),

        "currency": currency,

        "impact": impact,

        "title": title,

        "actual": actual,

        "forecast": forecast,

        "previous": previous,

        "direction": direction,

        "indicator_direction": indicator_direction,

        "strength": strength

    }


# =========================================================
# Main
# =========================================================

def main():

    print(
        "Downloading economic calendar..."
    )

    events = get_news()

    result = []

    for event in events:

        cleaned = clean_event(event)

        if cleaned is not None:

            result.append(
                cleaned
            )

    # ترتيب الأخبار حسب التاريخ
    result.sort(
        key=lambda x: x.get(
            "date",
            ""
        )
    )

    output = {

        "source": "ForexFactory",

        "source_type": "unofficial_feed",

        "updated": datetime.now(
            timezone.utc
        ).isoformat(),

        "count": len(result),

        "currencies": [
            "USD",
            "EUR",
            "GBP",
            "JPY",
            "CHF",
            "CAD",
            "AUD",
            "NZD"
        ],

        "impacts": [
            "High",
            "Medium",
            "Low"
        ],

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

    print(
        "Economic calendar updated successfully."
    )


if __name__ == "__main__":

    main()
