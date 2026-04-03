import requests
from datetime import datetime

CITY_TIMEZONE_MAP = {
    "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "london": "Europe/London",
    "new york": "America/New_York",
    "tokyo": "Asia/Tokyo",
    "dubai": "Asia/Dubai",
    "paris": "Europe/Paris",
    "sydney": "Australia/Sydney"
}

def get_time(city: str = "local") -> str:
    if city.lower() == "local":
        now = datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."

    try:
        city_lower = city.lower().strip()

        # 🔥 smart normalization
        if "delhi" in city_lower:
            city_lower = "delhi"

        timezone = CITY_TIMEZONE_MAP.get(city_lower)

        if not timezone:
            return f"Sorry, I don't recognize the city '{city}'."

        url = "https://www.timeapi.io/api/Time/current/zone"
        params = {"timeZone": timezone}

        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            time_str = data.get("dateTime")

            if time_str:
                dt = datetime.fromisoformat(time_str)
                formatted_time = dt.strftime("%I:%M %p")

                return f"The current time in {city.title()} is {formatted_time}."

        return f"Sorry, I couldn't fetch the time for {city}."

    except Exception as e:
        print("Time tool error:", e)
        return f"Sorry, I couldn't fetch the time for {city}."