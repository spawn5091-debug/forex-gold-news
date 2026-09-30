import json
from datetime import datetime, timezone

INPUT_FILE = "economic_calendar.json"
OUTPUT_FILE = "trading_signals.json"

PAIRS = {
    "XAUUSD": ("USD", None),
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDJPY": ("USD", "JPY"),
    "USDCHF": ("USD", "CHF"),
    "USDCAD": ("USD", "CAD"),
    "AUDUSD": ("AUD", "USD"),
    "NZDUSD": ("NZD", "USD"),
}

IMPACT_SCORE = {
    "High": 3,
    "Medium": 2,
    "Low": 1
}


def load_calendar():

    try:
        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print("ERROR loading calendar:", error)

        return {
            "events": []
        }


def parse_datetime(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    except Exception:
        return None


def get_currency_bias(events, currency):

    stronger = 0
    weaker = 0
    unknown = 0

    related_events = []

    for event in events:

        if event.get("currency") != currency:
            continue

        impact = event.get("impact", "Low")

        score = IMPACT_SCORE.get(
            impact,
            1
        )

        strength = event.get(
            "strength",
            "Unknown"
        )

        if strength == "Stronger":

            stronger += score

        elif strength == "Weaker":

            weaker += score

        else:

            unknown += score

        related_events.append({
            "title": event.get("title", ""),
            "datetime": event.get("datetime", ""),
            "impact": impact,
            "direction": event.get(
                "direction",
                "Unknown"
            ),
            "indicator_direction": event.get(
                "indicator_direction",
                "Neutral"
            ),
            "strength": strength
        })

    if stronger > weaker:

        bias = "Stronger"

    elif weaker > stronger:

        bias = "Weaker"

    else:

        bias = "Neutral"

    return {
        "currency": currency,
        "bias": bias,
        "stronger_score": stronger,
        "weaker_score": weaker,
        "unknown_score": unknown,
        "events": related_events
    }


def get_pair_bias(pair, currency_data):

    base_currency, quote_currency = PAIRS[pair]

    base = currency_data.get(
        base_currency,
        {}
    )

    base_bias = base.get(
        "bias",
        "Neutral"
    )

    if quote_currency is None:

        if base_bias == "Stronger":
            return "Bearish"

        if base_bias == "Weaker":
            return "Bullish"

        return "Neutral"

    quote = currency_data.get(
        quote_currency,
        {}
    )

    quote_bias = quote.get(
        "bias",
        "Neutral"
    )

    if (
        base_bias == "Stronger"
        and quote_bias != "Stronger"
    ):

        return "Bullish"

    if (
        quote_bias == "Stronger"
        and base_bias != "Stronger"
    ):

        return "Bearish"

    if (
        base_bias == "Weaker"
        and quote_bias != "Weaker"
    ):

        return "Bearish"

    if (
        quote_bias == "Weaker"
        and base_bias != "Weaker"
    ):

        return "Bullish"

    return "Neutral"


def main():

    print("Loading economic calendar...")

    calendar = load_calendar()

    events = calendar.get(
        "events",
        []
    )

    currencies = [
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "CHF",
        "CAD",
        "AUD",
        "NZD"
    ]

    currency_data = {}

    for currency in currencies:

        currency_data[currency] = (
            get_currency_bias(
                events,
                currency
            )
        )

    pair_data = {}

    for pair in PAIRS:

        pair_data[pair] = {
            "pair": pair,
            "bias": get_pair_bias(
                pair,
                currency_data
            )
        }

    output = {

        "source": "forex-gold-news",

        "updated": datetime.now(
            timezone.utc
        ).isoformat(),

        "currency_bias": currency_data,

        "pair_bias": pair_data,

        "pairs": [
            "XAUUSD",
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCHF",
            "USDCAD",
            "AUDUSD",
            "NZDUSD"
        ],

        "logic": {
            "XAUUSD": "USD stronger = Bearish Gold",
            "EURUSD": "EUR stronger = Bullish",
            "GBPUSD": "GBP stronger = Bullish",
            "USDJPY": "USD stronger = Bullish",
            "USDCHF": "USD stronger = Bullish",
            "USDCAD": "USD stronger = Bullish",
            "AUDUSD": "AUD stronger = Bullish",
            "NZDUSD": "NZD stronger = Bullish"
        }
    }

    with open(
        OUTPUT_FILE,
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
        "Trading signals saved:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
