from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def get_weather_forecast(location: str, days: int = 1) -> dict[str, Any]:
    """
    Fetch weather forecast for a specified location using Open-Meteo API.
    """
    if not location or not location.strip():
        return {
            "error": "Location parameter is required.",
            "message": "Missing location.",
            "items": [],
        }

    try:
        # Step 1: Geocoding to get lat & lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            geo_data = json.loads(response.read().decode("utf-8"))

        results = geo_data.get("results")
        if not results:
            return {
                "error": f"Location '{location}' not found.",
                "message": "Geocoding failed.",
                "items": [],
            }

        place = results[0]
        name = place.get("name")
        country = place.get("country", "")
        lat = place.get("latitude")
        lon = place.get("longitude")

        # Step 2: Query weather forecast
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto&forecast_days={min(max(days, 1), 7)}"
        req = urllib.request.Request(weather_url, headers={"User-Agent": "ResearchAgent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            weather_data = json.loads(response.read().decode("utf-8"))

        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        windspeed = current.get("windspeed")
        weathercode = current.get("weathercode")

        full_location = f"{name}, {country}".strip(", ")

        item = {
            "title": f"Weather forecast for {full_location}",
            "location": full_location,
            "latitude": lat,
            "longitude": lon,
            "temperature_celsius": temp,
            "windspeed_kmh": windspeed,
            "weather_code": weathercode,
            "summary": f"Current temperature in {full_location} is {temp}°C with wind speed of {windspeed} km/h.",
        }

        return {
            "error": None,
            "message": f"Successfully retrieved weather for {full_location}.",
            "items": [item],
            "location": full_location,
            "temperature": temp,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to fetch weather for '{location}'.",
            "items": [],
        }
