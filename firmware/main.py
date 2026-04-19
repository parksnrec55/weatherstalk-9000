import requests
from datetime import datetime, timezone

API_URL = "http://localhost:8000/weatherdata/"
LOCATION = "home"


# TODO: read temperature and humidity from the SparkFun sensor
def read_sensor():
    temp_f = 72.0
    humidity = 55.0
    return temp_f, humidity


def post_weather_data(temp: float, humidity: float):
    payload = {
        "location": LOCATION,
        "time": datetime.now(timezone.utc).isoformat(),
        "temp": temp,
        "humidity": humidity,
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    temp, humidity = read_sensor()
    result = post_weather_data(temp, humidity)
    print(f"Posted: {result}")
