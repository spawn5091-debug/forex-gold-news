import json
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

    if text in ("", "-", "—", "N/A", "NA", "None"):
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

    lower_is_stronger = [
        "unemployment claims",
        "jobless claims",
        "initial claims",
        "continuing claims",
        "unemployment rate",
        "unemployment",
        "jobless"
    ]

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

    neutral = [
        "interest rate decision",
        "cash rate",
        "fomc statement",
        "fomc",
        "ecb",
        "boe",
        "
