import json
import datetime
from pyowm import OWM
from pyowm.utils.config import get_default_config
import screen_brightness_control as sbc
import psutil


months = {
    "1": "января",
    "2": "февраля",
    "3": "марта",
    "4": "апреля",
    "5": "мая",
    "6": "июня",
    "7": "июля",
    "8": "августа",
    "9": "сентября",
    "10": "октрября",
    "11": "ноября",
    "12": "декабря"
}

weekdays = {
    "0": "Понедельник",
    "1": "Вторник",
    "2": "Среда",
    "3": "Четверг",
    "4": "Пятница",
    "5": "Суббота",
    "6": "Воскресенье",
}


class Functions:

    def __init__(self):
        API = 'd8103ddb4c9d11d7f82ffad9cce5ee36'  # Апи к сервису от погоды
        conf = get_default_config()  # Получение дефолтного конфига
        conf["language"] = 'ru'  # Изменить в конфиге язык на русский
        self.owm = OWM(API, conf)  # Применить новый конфиг и подключить апи


    def time(self):
        a = datetime.datetime.now()
        return f'Сейчас {a.hour}:{a.minute}'


    def date(self):
        a = datetime.datetime.now()
        return f'Сегодня {a.day} {months[str(a.month)]}, {weekdays[str(a.weekday()).lower()]}'


    def weather(self):
        place = 'Северодвинск'  # Задание места, по дефолту поставил Севск, но в будущем будет зависеть от настроек пользователя
        try:
            monitoring = self.owm.weather_manager().weather_at_place(place)  # Вырвано из доков
            weather = monitoring.weather  # Тоже вырвано из доков
            temp = weather.temperature('celsius')  # Получение температуры по цельсия
            status = weather.detailed_status  # Краткий статус погоды, типо "Облачно"
            return (f'Сейчас {int(temp["temp"])}°C, {status}')
        except:
            return f"Неверно указано место ({place})"


    def brightness_arg(self, text):  # Смена яркости
        text = f' {text} '
        for i in range(1, 101):
            if f' {i} ' in text:
                sbc.set_brightness(i)
                return f'Была установлена яркость в {i}%'
            else:
                continue
        return 'Не получилось выявить желаемый уровень яркости'
        # все штуки типо f" {} " нужны для правильной обработки, чтобы везде были разделения пробелами и не получалось багов типо: "восемь" -> "во7"

    def ram(self):
        rm = psutil.virtual_memory().percent
        return f'Текущая нагрузка на оперативную память {rm}%'

    def cpu(self):
        cp = psutil.cpu_percent()
        return f'Текущая нагрузка на процессор {cp}%'

    def volume_arg(self, text):
        pass  # Еще делаю


class Definer:

    def __init__(self):
        # Импорт датасета
        with open(r'data\cmd.json', 'r', encoding='utf-8') as file:
            self.cmd_list = json.load(file)

    # Функция для поиска в тексте фраз, для запуска команд
    def define(self, text):
        output = ''
        for command in self.cmd_list:
            for txt in self.cmd_list[command]:
                if txt in text:
                    print('Recognized command', command)  # Знаю, самое лучшее логирование
                    if output != '':
                        output = f'{output}\n{self.start_command(command, text)}'
                    else:
                        output = self.start_command(command, text)
                else:
                    continue
        if output != '':
            return output

    # Запуск команды по её названию
    # Если в названии команды есть постфикс "_arg" то она принимает аргумент в виде распознанного текста, чтобы его
    # обрабатывать на предмет нужных данных
    def start_command(self, cmd, arg):
        if str(cmd).endswith('_arg') is False:  # Проверка на постфикс
            out = eval(f'Functions().{cmd}()')  # Запуск команды без аргумента
        else:
            out = eval(f'Functions().{cmd}("{arg}")')  # Запуск команды с аргументом
        return out  # Возврат вывода вызванной функции
