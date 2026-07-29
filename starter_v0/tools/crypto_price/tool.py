from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def get_crypto_price(symbol: str, currency: str = "usd") -> dict[str, Any]:
    """
    Get current market price of a cryptocurrency using CoinGecko API.
    """
    if not symbol or not symbol.strip():
        return {
            "error": "Symbol parameter is required (e.g. bitcoin, ethereum, solana).",
            "message": "Missing crypto symbol.",
            "items": [],
        }

    coin_id = symbol.strip().lower()
    target_currency = currency.strip().lower()

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={urllib.parse.quote(coin_id)}&vs_currencies={target_currency}"
        req = urllib.request.Request(url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if coin_id not in data or target_currency not in data[coin_id]:
            return {
                "error": f"Price data for cryptocurrency '{symbol}' in '{currency}' not found.",
                "message": "Symbol or currency not found.",
                "items": [],
            }

        price = data[coin_id][target_currency]

        item = {
            "title": f"Crypto Price: {coin_id.upper()} / {target_currency.upper()}",
            "symbol": coin_id,
            "currency": target_currency,
            "price": price,
            "summary": f"Current price of {coin_id.capitalize()} is {price} {target_currency.upper()}.",
        }

        return {
            "error": None,
            "message": f"Successfully retrieved price for {coin_id}.",
            "items": [item],
            "symbol": coin_id,
            "currency": target_currency,
            "price": price,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to fetch crypto price for '{symbol}'.",
            "items": [],
        }
