# -*- coding: utf-8 -*-

# Импорт библиотек
import os
import os.path
import pyaudio
import sounddevice as sd
import time
import torch
from PyQt5 import QtCore
from vosk import KaldiRecognizer, Model
import datetime
from pyowm import OWM
import json
from pyowm.utils.config import get_default_config
import screen_brightness_control as sbc
from text_to_num import stn
import psutil
from logs import Logger
from rss_parser import Parser
from requests import get
import random

loger = Logger()


def benchmark(func):
	def wrapper(*args, **kwargs):
		start = time.time()
		return_value = func(*args, **kwargs)
		end = time.time()
		print('[*] Время выполнения: {} секунд.'.format(end - start))
		return return_value

	return wrapper


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


# текст выдаваемый vosk выдается как словарь, но в виде строки, поэтому я просто очищаю ее пока не останется лишь сам текст
def clean(text):
	text = text.replace('\n', '')
	text = text.replace('{  "partial" : "', '')
	text = text.replace('{  "text" : "', '')
	text = text.replace('"}', '')
	return text


# Класс для определения и запуска функций в исходном тексте
class Definer:
	def __init__(self):

		# Импорт датасета
		if os.path.exists(r'data\cmd.json'):
			pass
		else:
			loger.fatal_err(
				'Dataset hasn\'t be found')  # Если не нашел датасет, просто прога превращается в кирпич и ничего не делает (я не смог отсюда закрыть окно)
			raise SystemExit()

		with open(r'data\cmd.json', 'r', encoding='utf-8') as file:
			self.cmd_list = json.load(file)

	# Функция для поиска в тексте фраз, для запуска команд
	def define(self, text):
		output = ''
		for command in self.cmd_list:
			for txt in self.cmd_list[command]:
				if txt in text:
					loger.log(f'Recognized command: {command}')  # Знаю, самое лучшее логирование
					if output != '':
						output = f'{output}\n{self.start_command(command, text)}'
					else:
						output = self.start_command(command, text)
				else:
					continue
		if output != '':
			return output

	# Запуск команды по её названию
	# Если в названии команды есть постфикс "_arg" то она принимает аргумент в виде распознанного текста, чтобы
	# его обрабатывать на предмет нужных данных
	def start_command(self, cmd, arg):
		if str(cmd).endswith('_arg') is False:  # Проверка на постфикс
			out = eval(f'Functions().{cmd}()')  # Запуск команды без аргумента
		else:
			out = eval(f'Functions().{cmd}("{arg}")')  # Запуск команды с аргументом
		return out  # Возврат вывода вызванной функции


# Класс с основными функциями которые выполняются по команде пользователя
class Functions:
	def __init__(self):
		API = 'd8103ddb4c9d11d7f82ffad9cce5ee36'  # Апи к сервису от погоды
		conf = get_default_config()  # Получение дефолтного конфига
		conf["language"] = 'ru'  # Изменить в конфиге язык на русский
		try:
			self.owm = OWM(API, conf)  # Применить новый конфиг и подключить апи
		except:
			loger.warning('Отстутствует подключение к интернету')
			self.owm = None

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
			return f"Неверно указано место ({place}) и/или отсутствует подключение к интернету"

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
		pass # Еще делаю

	def news(self):

		titles = []

		rss_url = "https://habr.com/ru/rss/news/?fl=ru"
		xml = get(rss_url)

		parser = Parser(xml=xml.content, limit=10)
		feed = parser.parse()

		for new in reversed(feed.feed):
			titles.append(new)
		item = random.choice(titles)
		return f'Заговолок: {item.title}\nСодержимое: {item.description.replace("Читать дальше →", "").replace("Читать далее", "")}'

# Класс с функцией синтеза речи
class TextToSpeech:
	def __init__(self):
		device = torch.device('cpu') # гпу или цпу
		try:
			# Загрузка языковой модели, чтобы после первого скачивания использовать ее без интернета
			self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
										   model='silero_tts',
										   language='ru',
										   speaker='ru_v3')
			self.model.to(device)
		except Exception as e:
			loger.fatal_err(e)

	@benchmark
	def say(self, audio):
		audio = self.model.apply_tts(text=audio,
									 speaker='kseniya')  # Синтез речи
		# Воспроизведение синтеза
		sd.play(audio, 48000)
		time.sleep(len(audio) / 48000)
		sd.stop()


# Распознавание речи через заранее установленную языковую модель
# Этот класс наследует другой класс, который может отправлять сигналы
# для работы в нескольких потоках
class RecordThreadHandler(QtCore.QThread):
	tts = TextToSpeech()
	signal = QtCore.pyqtSignal(list) # Инициализация этого сигнала
	handler_status: bool = True # Активна ли функция распознавания
	# Много всякой инициализации
	path = os.getcwd() + r'\data\vosk-model-small-ru-0.22'
	if os.path.exists(path):
		pass
	else:
		loger.fatal_err('Vosk model hasn\'t be found')
		raise SystemExit()
	model = Model(path)
	rec = KaldiRecognizer(model, 16000)
	p = pyaudio.PyAudio()
	stream = p.open(
		format=pyaudio.paInt16,
		channels=1,
		rate=16000,
		input=True,
		frames_per_buffer=8000
	)

	# Запуск распознавания
	def run(self):

		self.signal.emit(['start_thread'])

		while True:
			try:
				while self.handler_status:
					self.stream.start_stream()  # начать слушать
					data = self.stream.read(2000, exception_on_overflow=False)
					if len(data) == 0: # Если никакого звука нет (Но редко работает, т.к. всегда есть микрошумы)
						self.stream.stop_stream()
						break
					if self.rec.AcceptWaveform(data) and self.handler_status:
						txt = clean(self.rec.Result()).capitalize() # Получение очищенной фразы
						if txt != '': # Если хоть что-то распозналось
							self.stream.stop_stream() # Прекращение записи
							txt = stn(txt.lower()) # изменить в тексте все названия чисел на сами числа (работает лишь от нуля до 100, но пока-что больше не надо)
							loger.log(f'Recognized text: {txt}')
							self.signal.emit(['user_responce', txt]) # Сигнал о распознанном тексте, чтобы вкинуть его в интерфейс
							output = str(Definer().define(txt.lower()))  # Запускаем обработку распознанной реплики пользователя
							loger.log(f'Bot\'s answer: {output}')
							if output != 'None':
								#Thread(target=lambda: self.tts.say(audio=output)).start()
								#self.tts.say(output)
								self.signal.emit(['bot_responce', output])

							continue
						else:
							continue
				else:
					break
			except Exception as e:
				loger.warning(e)


# Оставляю это место чтобы быстро проверять функции
if __name__ == "__main__":
	pass
