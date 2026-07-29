from __future__ import annotations

import json
import urllib.request
from typing import Any


def convert_currency(from_currency: str, to_currency: str, amount: float = 1.0) -> dict[str, Any]:
    """
    Convert amount from one currency to another using ExchangeRate Open API.
    """
    if not from_currency or not to_currency:
        return {
            "error": "Both from_currency and to_currency parameters are required.",
            "message": "Missing currency codes.",
            "items": [],
        }

    base_curr = from_currency.strip().upper()
    target_curr = to_currency.strip().upper()

    try:
        url = f"https://open.er-api.com/v6/latest/{base_curr}"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("result") != "success":
            return {
                "error": f"Failed to retrieve exchange rates for base currency '{base_curr}'.",
                "message": data.get("error-type", "API error"),
                "items": [],
            }

        rates = data.get("rates", {})
        if target_curr not in rates:
            return {
                "error": f"Target currency '{target_curr}' not supported.",
                "message": "Currency not found.",
                "items": [],
            }

        rate = rates[target_curr]
        converted = round(amount * rate, 4)

        item = {
            "title": f"Currency Conversion: {amount} {base_curr} to {target_curr}",
            "from_currency": base_curr,
            "to_currency": target_curr,
            "amount": amount,
            "exchange_rate": rate,
            "converted_amount": converted,
            "summary": f"{amount} {base_curr} = {converted} {target_curr} (Rate: 1 {base_curr} = {rate} {target_curr})",
        }

        return {
            "error": None,
            "message": f"Successfully converted {amount} {base_curr} to {converted} {target_curr}.",
            "items": [item],
            "from_currency": base_curr,
            "to_currency": target_curr,
            "amount": amount,
            "converted_amount": converted,
            "rate": rate,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to convert {base_curr} to {target_curr}.",
            "items": [],
        }
