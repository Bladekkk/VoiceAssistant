from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui

from alpha import Ui_MainWindow
from methods import RecordThreadHandler, FileWatcherThread, TextToSpeech
from logs import cur_time

import time
from threading import Thread

class Widget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._old_pos = None
        self.btn_close.clicked.connect(self.close)
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.Switch.clicked.connect(self.start_record)
        self.List.setWordWrap(True)
        self.sets_btn.clicked.connect(self.resizer)
        self.horizontalSlider.valueChanged.connect(lambda: self.setWindowOpacity(self.horizontalSlider.value() / 100))

        self.thread_handler = RecordThreadHandler()
        self.thread_handler.signal.connect(self.signal_handler)

        time1, date = cur_time()
        self.log_file = f'log/{date}/{time1}.txt'
        self.file_watcher = FileWatcherThread(self.log_file)
        self.file_watcher.file_changed.connect(self.update_text_edit)

        self.file_watcher.start()

        self.active_status = False

        self.font = QtGui.QFont()
        self.font.setFamily("System")
        self.font.setPointSize(10)

        self.tts = TextToSpeech()

    def say1(self, text):
        self.thread_handler.isFree = False
        self.tts.say(text)
        time.sleep(1)
        self.thread_handler.isFree = True

    def resizer(self):
        a = str(self.size()).replace('PyQt5.QtCore.QSize(', '').replace(')', '')
        if a == '350, 620':
            self.resize(690, 620)
        else:
            self.resize(350, 620)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = None

    def mouseMoveEvent(self, event):
        if not self._old_pos:
            return
        delta = event.pos() - self._old_pos
        self.move(self.pos() + delta)

    def start_record(self):
        if not self.active_status:
            self.signal_handler(['start_thread'])
            self.thread_handler.handler_status = True
            self.thread_handler.start()

        else:
            self.signal_handler(['bot_exit'])
            self.thread_handler.handler_status = False

    def update_text_edit(self, text) -> None:
        self.logs_plain.setPlainText(text)

    def signal_handler(self, value: list) -> None:
        if value[0] == 'start_thread':
            self.active_status = True
            self.status.setStyleSheet("background-color: rgb(127, 216, 170);")

        elif value[0] == 'user_responce':
            user_resp = QListWidgetItem()
            user_resp.setTextAlignment(Qt.AlignLeft)
            user_resp.setText(f"\n[Вы]\n{value[1]}")
            user_resp.setForeground(Qt.black)
            user_resp.setFont(self.font)
            self.List.addItem(user_resp)
            self.List.scrollToBottom()

        elif value[0] == 'bot_responce':
            output = str(value[1])
            if output != 'None':
                Thread(target=lambda: self.say1(output)).start()
                bot_resp = QListWidgetItem()
                bot_resp.setTextAlignment(Qt.AlignRight)
                bot_resp.setForeground(Qt.black)
                bot_resp.setFont(self.font)
                bot_resp.setText(f"\n[Бот]\n{output}")
                self.List.addItem(bot_resp)
                self.List.scrollToBottom()

        elif value[0] == 'bot_exit':
            self.thread_handler.handler_status = False
            self.active_status = False
            self.status.setStyleSheet("background-color: rgb(209, 123, 117);")

        elif value[0] == 'stop_program':
            self.close()


if __name__ == '__main__':
    app = QApplication([])

    w = Widget()
    w.resize(350, 620)
    w.show()

    app.exec()

