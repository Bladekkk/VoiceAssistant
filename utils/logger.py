import datetime
import os.path
from pathlib import Path

def cur_time():
    now = datetime.datetime.now()
    min = str(now.minute)
    if len(min) == 1:
        min = f'0{min}'
    hour = str(now.hour)
    if len(hour) == 1:
        hour = f'0{hour}'
    return f'{hour}-{min}', now.date()

def get_project_root():
    """Возвращает абсолютный путь к корню проекта"""
    current_file = Path(__file__).resolve()
    # Поднимаемся на уровни пока не найдем корень (можно настроить)
    for parent in current_file.parents:
        if (parent / 'main.py').exists() or (parent / 'requirements.txt').exists():
            return parent
    return current_file.parent.parent  # Fallback

class Logger:

    def __init__(self):
        project_root = get_project_root()
        log_dir = project_root / 'log'
        self.log_dir = str(log_dir)

        time, date = cur_time()
        self.log_file = str(log_dir / f'{date}' / f'{time}.txt')



    def basic_log(self, type, text):
        time, date = cur_time()
        log = f'[{time.replace("-", ":")}:{datetime.datetime.now().second}][{type}]: {text}'
        print(log)
        if os.path.exists(self.log_dir):
            pass
        else:
            os.mkdir(self.log_dir)

        if os.path.exists(f'{self.log_dir}\\{date}'):
            pass
        else:
            os.mkdir(f'{self.log_dir}\\{date}')

        if os.path.exists(self.log_file):
            with open(self.log_file, 'a') as f:
                f.write(f'\n{log}')
        else:
            with open(self.log_file, 'w') as f:
                f.write(log)


    def log(self, text):
        self.basic_log('Log', text)


    def warning(self, text):
        self.basic_log('Warning', text)

    def error(self, text):
        self.basic_log('Error', text)

if __name__ == "__main__":
    Logger().log('It\'s just a log')
    Logger().warning('It\'s a warning!')
    Logger().fatal_err('It\'s a error!!!')
