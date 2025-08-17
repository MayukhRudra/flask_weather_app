import requests
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()
api_key = os.getenv('API_KEY')

@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temperature: int

def get_lan_lon(city_name, state_code, country_code, API_key):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}').json()
    data = resp[0]
    lat, lon = data.get('lat'), data.get('lon')
    return lat, lon

def get_location_name(lat, lon, API_key):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_key}').json()
    if resp:
        city = resp[0].get('name', '')
        state = resp[0].get('state', '')
        country = resp[0].get('country', '')
        return f"{city}, {country}" if city else "Unknown"
    return "Unknown"

def get_location_parts(lat, lon, API_key):
    resp = requests.get(
        f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_key}'
    ).json()
    if resp:
        city = resp[0].get('name', '')
        state = resp[0].get('state', '')
        country = resp[0].get('country', '')
        return city, state, country
    return '', '', ''

def get_coords_metadata(lat, lon):
    city, state, country = get_location_parts(lat, lon, api_key)
    return {
        'city': city,
        'state': state,
        'country': country
    }

def get_weather_by_coords(lat, lon):
    current = get_current_weather(lat, lon, api_key)
    hourly, daily = get_forecasts(lat, lon, api_key)
    pollution = get_air_pollution(lat, lon, api_key)
    location_name = get_location_name(lat, lon, api_key)
    return {'current': current, 'hourly': hourly, 'forecast': daily, 'pollution': pollution, 'location_name': location_name}
    
def get_current_weather(lat, lon, API_key):
    resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric').json()
    data = WeatherData(
        main=resp.get('weather')[0].get('main'),
        description=resp.get('weather')[0].get('description'),
        icon=resp.get('weather')[0].get('icon'),
        temperature=int(resp.get('main', {}).get('temp')))
    return data

def get_forecasts(lat, lon, API_key):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_key}&units=metric'
    resp = requests.get(url).json()

    hourly_forecast = []
    daily_forecast = []

    for item in resp.get('list', []):
        if len(hourly_forecast) < 6:
            hourly_forecast.append({
                'time': item['dt_txt'].split(' ')[1][:5],
                'temperature': int(item['main']['temp']),
                'main': item['weather'][0]['main'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
            })
        if "12:00:00" in item['dt_txt']:
            daily_forecast.append({
                'date': item['dt_txt'].split(' ')[0],
                'temperature': int(item['main']['temp']),
                'main': item['weather'][0]['main'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon'],
            })

        if len(daily_forecast) == 3:
            break

    return hourly_forecast, daily_forecast

def get_air_pollution(lat, lon, API_key):
    url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_key}'
    resp = requests.get(url).json()
    if "list" not in resp:
        return None

    data = resp["list"][0]
    aqi = data["main"]["aqi"]  # 1 to 5 scale
    components = data["components"]

    return {
        "aqi": aqi,
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "co": components.get("co"),
        "no2": components.get("no2"),
        "so2": components.get("so2"),
        "o3": components.get("o3")
    }
        
def main(city_name, state_name, country_name):
    lat, lon = get_lan_lon(city_name, state_name, country_name, api_key)
    if lat is None or lon is None:
        return None
    current = get_current_weather(lat, lon, api_key)
    hourly, daily = get_forecasts(lat, lon, api_key)
    pollution = get_air_pollution(lat, lon, api_key)
    return {'current': current, 'hourly': hourly, 'forecast': daily, 'pollution': pollution}

if __name__ == "__main__":
    lat, lon =get_lan_lon('Kolkata', 'ON', 'India', api_key)
    print(get_current_weather(lat, lon, api_key))