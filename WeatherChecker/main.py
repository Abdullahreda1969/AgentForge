import requests
import json

def get_weather(city):
    """
    Retrieves the current weather data for a given city using the python-weather library.

    Args:
        city (str): The name of the city to get the weather for.

    Returns:
        dict: A dictionary containing the weather data, or None if an error occurs.
    """
    try:
        url = f"https://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY&q={city}"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None

if __name__ == "__main__":
    city = input("Enter the city name: ")
    weather_data = get_weather(city)

    if weather_data:
        print(f"Current weather in {city}:")
        print(f"Temperature: {weather_data['temp']}°C")
        print(f"Feels like: {weather_data['feels_like']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind: {weather_data['wind'][0]} m/s")
        print(f"Description: {weather_data['description']}")
    else:
        print("Could not retrieve weather data.")