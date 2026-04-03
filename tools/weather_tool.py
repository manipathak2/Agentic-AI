import requests

def get_weather(city: str) -> str:
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1}

        geo_res = requests.get(geo_url, params=geo_params, timeout=5)
        geo_data = geo_res.json()

        if not geo_data.get("results"):
            return f"Sorry, I couldn't find the location '{city}'."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        city_name = geo_data["results"][0]["name"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }

        weather_res = requests.get(weather_url, params=weather_params, timeout=5)
        weather_data = weather_res.json()

        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        wind = current.get("windspeed")

        return (
            f"Currently in {city_name}, the temperature is {temp}°C "
            f"with wind speed {wind} km/h."
        )

    except Exception as e:
        print("Weather tool error:", e)
        return "Sorry, I couldn't fetch the weather right now."