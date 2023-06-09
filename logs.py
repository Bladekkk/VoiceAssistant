import datetime
import os.path

def cur_time():
    now = datetime.datetime.now()
    min = str(now.minute)
    if len(min) == 1:
        min = f'0{min}'
    hour = str(now.hour)
    if len(hour) == 1:
        hour = f'0{hour}'
    return f'{hour}-{min}', now.date()

class Logger:

    def __init__(self):
        if os.path.exists('log'):
            pass
        else:
            os.mkdir('log')
        time, date = cur_time()
        self.log_file = f'log/{date}/{time}.txt'
        self.log_dir = f'log/{date}'



    def basic_log(self, type, text):
        time, date = cur_time()
        log = f'[{time.replace("-", ":")}:{datetime.datetime.now().second}][{type}]: {text}'
        print(log)
        if os.path.exists(self.log_dir):
            pass
        else:
            os.mkdir(self.log_dir)
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

    def fatal_err(self, text):
        self.basic_log('Error', text)

if __name__ == "__main__":
    Logger().log('It\'s just a log')
    Logger().warning('It\'s a warning!')
    Logger().fatal_err('It\'s a error!!!')
