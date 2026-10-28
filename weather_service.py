import requests

API_KEY = "8a5648b7ce68c3f57de3f6cf3b499811"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather_by_city(city_name):
    """
    Виконує GET-запит до OpenWeatherMap API за назвою міста,
    перетворює дані у зручний формат та обробляє можливі помилки.
    """
    params = {
        'q': city_name.strip(),
        'appid': API_KEY,
        'units': 'metric'  #щоб температура була в градусах Цельсія
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)

        if response.status_code == 404:
            return {"error": f"Місто '{city_name}' не знайдено в базі даних API"}
        elif response.status_code != 200:
            return {"error": f"Помилка сервера API для міста {city_name}: код {response.status_code}"}

        data = response.json()

        #перетворення сирих даних у чисту структуру для нашого застосунку
        weather_info = {
            "city_name": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "condition": data.get("weather", [{}])[0].get("description", ""),
            "external_id": data.get("id"),
            "icon": data.get("weather", [{}])[0].get("icon", "")
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        return {"error": "Помилка мережі: не вдалося підключитися до зовнішнього API"}


def get_multiple_cities_weather(cities_str):
    """
    Приймає рядок міст через кому (наприклад, 'Vienna, Bratislava, Prague'),
    робить запит для кожного та повертає список успішних результатів.
    """
    city_names = [c.strip() for c in cities_str.split(',') if c.strip()]
    results = []
    errors = []

    for city in city_names:
        res = get_weather_by_city(city)
        if "error" in res:
            errors.append(res["error"])
        else:
            results.append(res)

    return results, errors