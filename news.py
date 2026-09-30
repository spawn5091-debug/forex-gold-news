import json
import re
import requests
from datetime import datetime, timezone

API_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

CURRENCIES = {
    "USD", "EUR", "GBP", "JPY",
    "CHF", "CAD", "AUD", "NZD"
}

IMPACTS = {
    "High", "Medium", "Low"
}


def clean_number(value):

    if value is None:
        return None

    text = str(value).strip()

    if text in ["", "-", "—", "N/A", "NA", "None"]:
        return None

    text = text.replace(",", "")
    text = text.replace("$", "")
    text = text.replace("%", "")
    text = text.replace(" ", "")

    multiplier = 1

    if text.upper().endswith("K"):
        multiplier = 1000
        text = text[:-1]

    elif text.upper().endswith("M"):
        multiplier = 1000000
        text = text[:-1]

    elif text.upper().endswith("B"):
        multiplier = 1000000000
        text = text[:-1]

    try:
        return float(text) * multiplier

    except Exception:
        return None


def get_direction(actual, forecast):

    actual_value = clean_number(actual)
    forecast_value = clean_number(forecast)

    if actual_value is None or forecast_value is None:
        return "Unknown"

    if actual_value > forecast_value:
        return "Higher"

    if actual_value < forecast_value:
        return "Lower"

    return "Neutral"


def get_indicator_direction(title):

    title = title.lower().strip()

    # Lower = Stronger
    lower_is_stronger = [
        "unemployment claims",
        "jobless claims",
        "initial claims",
        "continuing claims",
        "unemployment rate",
        "unemployment",
        "jobless"
    ]

    # Higher = Stronger
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
        "wages"
    ]

    # Neutral / لا نحاول تحديد قوة العملة تلقائياً
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
        "central bank",
        "cpi",
        "core cpi",
        "pce",
        "core pce",
        "inflation",
        "ppi",
        "core ppi",
        "trade balance",
        "budget balance"
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


def get_strength(direction, indicator_direction):

    if direction == "Unknown":
        return "Unknown"

    if indicator_direction == "Neutral":
        return "Neutral"

    if indicator_direction == "Higher":

        if direction == "Higher":
            return "Stronger"

        if direction == "Lower":
            return "Weaker"

    if indicator_direction == "Lower":

        if direction == "Lower":
            return "Stronger"

        if direction == "Higher":
            return "Weaker"

    return "Unknown"


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

    except Exception as error:

        print("ERROR:", error)
        return []


def clean_event(event):

    currency = str(
        event.get(
            "country",
            event.get(
                "currency",
                ""
            )
       
