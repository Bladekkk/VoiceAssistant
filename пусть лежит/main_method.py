from PyQt5 import QtCore
import time
from vosk import KaldiRecognizer, Model
import os
import pyaudio
from text_to_num import stn
from methods.TextToSpeech import TextToSpeech
from methods.Definer import Definer


# Декоратор, чтобы проверить функции на скорость выполнения
def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return return_value

    return wrapper


# текст выдаваемый vosk выдается как словарь, но в виде строки, поэтому я просто очищаю ее пока не останется лишь сам текст
def clean(text):
    text = text.replace('\n', '')
    text = text.replace('{  "partial" : "', '')
    text = text.replace('{  "text" : "', '')
    text = text.replace('"}', '')
    return text


# Распознавание речи через заранее установленную языковую модель
# Этот класс наследует другой класс, который может отправлять сигналы
# для работы в нескольких потоках
class RecordThreadHandler(QtCore.QThread):
    tts = TextToSpeech()
    signal = QtCore.pyqtSignal(list)  # Инициализация этого сигнала
    handler_status: bool = True  # Активна ли функция распознавания
    # Много всякой инициализации
    path = os.getcwd() + r'\data\vosk-model-small-ru-0.22'
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
                # print('[Log]: Слушаю') # Опять лучшее логирование
                while self.handler_status:
                    self.stream.start_stream()  # начать слушать
                    data = self.stream.read(2000, exception_on_overflow=False)
                    if len(data) == 0:  # Если никакого звука нет (Но редко работает, т.к. всегда есть микрошумы)
                        self.stream.stop_stream()
                        break
                    if self.rec.AcceptWaveform(data) and self.handler_status:
                        txt = clean(self.rec.Result()).capitalize()  # Получение очищенной фразы
                        if txt != '':  # Если хоть что-то распозналось
                            self.stream.stop_stream()  # Прекращение записи
                            txt = stn(txt.lower())  # изменить в тексте все названия чисел на сами числа (работает лишь от нуля до 100, но пока-что больше не надо)
                            print('Recognized text:', txt)  # Еще лучших логов
                            self.signal.emit(
                                ['user_responce', txt])  # Сигнал о распознанном тексте, чтобы вкинуть его в интерфейс
                            output = str(
                                Definer().define(txt.lower()))  # Запускаем обработку распознанной реплики пользователя
                            print(output)
                            if output != 'None':
                                # Thread(target=lambda: self.tts.say(audio=output)).start()
                                self.signal.emit(['bot_responce', output])
                                #self.tts.say(output) # Синтез речи

                            continue
                        else:
                            continue
                else:
                    break
            except Exception as e:
                print(f'Error: {e}')  # И опять самые классные логи, надо уже адекватно все переделать
