from pyowm import OWM
from pyowm.utils.config import get_default_config
from utils.logger import Logger

logger = Logger()

class WeatherService():
    def __init__(self, api_key: str, default_city: str = "Северодвинск"):
        self.api_key = api_key
        self.default_city = default_city
        self.owm = None
        self._initialize_owm()

    def _initialize_owm(self):
        """Инициализация клиента OWM"""
        try:
            conf = get_default_config()
            conf["language"] = 'ru'
            self.owm = OWM(self.api_key, conf)
            logger.log("Weather service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            self.owm = None

    def get_weather(self, city: str = None) -> str:
        """
        Получить погоду для указанного города
        :param city: название города (если None, используется город по умолчанию)
        :return: строка с описанием погоды
        """
        if not self.owm:
            return "Нет подключения к интернету для получения погоды"

        place = city or self.default_city

        try:
            monitoring = self.owm.weather_manager().weather_at_place(place)
            weather = monitoring.weather
            temp = weather.temperature('celsius')
            status = weather.detailed_status
            return f'Сейчас в {place} {int(temp["temp"])}°C, {status}'
        except Exception as e:
            logger.error(f"Weather error for {place}: {e}")
            return f"Не удалось получить погоду для {place}"

