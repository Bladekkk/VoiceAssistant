import torch
import time
import sounddevice as sd
import Logger from logs


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return return_value

    return wrapper


class TextToSpeech:
    def __init__(self):
        self.working = True
        device = torch.device('cpu')  # гпу или цпу
        try:
            # Загрузка языковой модели, чтобы после первого скачивания использовать ее без интернета
            self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                           model='silero_tts',
                                           language='ru',
                                           speaker='ru_v3')
            self.model.to(device)
        except Exception as e:
              # если не будет интернета для модели, или что-нибудь такое, потом сделаю нормальное логирование


    @benchmark
    def say(self, audio):
        # print('Начало синтеза')
        audio = self.model.apply_tts(text=audio,
                                     speaker='kseniya')  # Синтез речи
        print('Конец синтеза')
        # Воспроизведение синтеза
        sd.play(audio, 48000)
        time.sleep(len(audio) / 48000)
        sd.stop()
