import requests
import json
import os
from datetime import datetime
# Load the config file containing telegram credentials and location
with open("config.json") as f:
    config = json.load(f)
TELEGRAM_BOT_TOKEN = config["telegram_bot_token"]
TELEGRAM_CHAT_ID = config["telegram_chat_id"]
LAT = config["lat"]
LON = config["lon"]
OWM_API_KEY = config["openweather_api_key"]
WAPI_KEY = config["weatherapi_key"]
IQAIR_API_KEY = config["iqair_api_key"]

def get_openmeteo_forecast(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation_probability&forecast_days=1"
    )
    res = requests.get(url)
    data = res.json()
    try:
        rain_probs = data["hourly"]["precipitation_probability"][:2]
        for prob in rain_probs:
            if prob >= 50: 
                return True
        return False
    except KeyError:
        return False

def get_weatherapi_forecast(lat, lon, api_key):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{lon}&hours=6"
    res = requests.get(url)
    data = res.json()
    for hour in data["forecast"]["forecastday"][0]["hour"][:2]:
        if hour["will_it_rain"] == 1:
            return True
    return False

def get_weatherapi_detailed_forecast(lat, lon, api_key):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{lon}&days=1&aqi=no&alerts=no"
    res = requests.get(url)
    data = res.json()
    hourly_data = data["forecast"]["forecastday"][0]["hour"]

    # Get current hour block
    now_hour = datetime.utcnow().hour
    current_block = next((h for h in hourly_data if int(h["time"].split(" ")[1].split(":")[0]) == now_hour), hourly_data[0])

    return {
        "temp_c": current_block["temp_c"],
        "humidity": current_block["humidity"],
        "cloud": current_block["cloud"],
        "wind_kph": current_block["wind_kph"],
        "uv": current_block["uv"],
        "chance_of_rain": current_block["chance_of_rain"],
        "will_it_rain": current_block["will_it_rain"],
        "time": current_block["time"]
    }

def get_iqair_pollution_weather(lat, lon, api_key):
    url = f"https://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "success":
        raise Exception("Failed to fetch from IQAir API")

    pollution = data["data"]["current"]["pollution"]
    weather = data["data"]["current"]["weather"]

    return {
        "aqi_us": pollution["aqius"],
        "main_pollutant": pollution["mainus"],
        "temperature": weather["tp"],   # Celsius
        "humidity": weather["hu"],      # %
        "wind_speed": weather["ws"],    # m/s
        "timestamp": pollution["ts"]
    }

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    print("Telegram response:", response.status_code, response.text)

def lambda_handler(event=None, context=None):
    rain_openmeteo = get_openmeteo_forecast(LAT, LON)
    rain_wapi = get_weatherapi_forecast(LAT, LON, WAPI_KEY)
    forecast = get_weatherapi_detailed_forecast(LAT, LON, WAPI_KEY)
    pollution_weather = get_iqair_pollution_weather(LAT, LON, IQAIR_API_KEY)
    message = (
        f"🌤️ *Weather Update*\n\n"
        f"🕓 Time: {forecast['time']}\n"
        f"🌡️ Temperature: {forecast['temp_c']}°C\n"
        f"💧 Humidity: {forecast['humidity']}%\n"
        f"☁️ Cloud Cover: {forecast['cloud']}%\n"
        f"💨 Wind Speed: {forecast['wind_kph']} km/h\n"
        f"🔆 UV Index: {forecast['uv']}\n"
        f"🌧️ Rain Chance: {forecast['chance_of_rain']}%\n"
    )
    message += (
        f"\n🌫️ *Air Quality (US AQI)*: {pollution_weather['aqi_us']} (Main: {pollution_weather['main_pollutant'].upper()})"
    )
    if rain_openmeteo or rain_wapi:
        send_telegram_message(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
            f"Rain is predicted in your area in the next few hours. Carry an umbrella! Plan your travel!\n\n{message}"
        )
    elif forecast['chance_of_rain'] > 50:
        send_telegram_message(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
            f"There is a high chance of rain in your area\n\n{message}"
        )
    else:
        send_telegram_message(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
            f"No Rain Predicted for your area\n\n{message}"
        )


    return {
        "statusCode": 200,
        "body": json.dumps("Check complete")
    }

