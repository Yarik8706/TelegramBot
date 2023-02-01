from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

owm = OWM("ds")
mgr = owm.weather_manager()

observation = mgr.weather_at_place('London,GB')
w = observation.weather

print(w.temperature('celsius')) # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

class WeatherController:


    def __init__(self, api_key):
        self.own = OWM(api_key)


    def get_weather_by_name(self, city_name):
        pass
