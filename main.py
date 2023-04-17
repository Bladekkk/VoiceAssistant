from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

from ui import Ui_MainWindow
from methods import RecordThreadHandler



class Widget(QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.setWindowFlags(Qt.FramelessWindowHint) # Убираем системные рамки + кнопки: закрыть, свернуть
		self.setAttribute(Qt.WA_TranslucentBackground) # Убираем фон который выходит за круглые рамки, чтобы выглядело красиво

		self._old_pos = None
		self.btn_close.clicked.connect(self.close)
		self.btn_minimize.clicked.connect(self.showMinimized)
		self.Switch.clicked.connect(self.start_record)
		self.List.setWordWrap(True)

		self.thread_handler = RecordThreadHandler()
		self.thread_handler.signal.connect(self.signal_handler)

		self.active_status = False

		self.font = QtGui.QFont()
		self.font.setFamily("Arial Black")
		self.font.setPointSize(10)

		self.setWindowOpacity(0.75) # Прозрачность окна (от 0 до 1, float)

	# Следующие функции для того чтобы переносить окно за любое место
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

	# Нажимается кнопка вкл\выкл, по ситуации либо включаем распознавание, либо останавливаем
	def start_record(self):
		if self.active_status is False:
			self.signal_handler(['start_thread'])
			self.thread_handler.handler_status = True
			self.thread_handler.start()

		elif self.active_status is True:
			self.signal_handler(['bot_exit'])
			self.thread_handler.handler_status = False

	def signal_handler(self, value: list) -> None:
		if value[0] == 'start_thread':
			self.active_status = True
			self.status.setStyleSheet("background-color: rgb(127, 216, 170);") # Меняем цвет кнопки

		elif value[0] == 'user_responce':
			user_resp = QListWidgetItem()  # Создаем объект со стороны пользователя
			user_resp.setTextAlignment(Qt.AlignLeft)
			user_resp.setText(f"[Вы]\n{value[1]}")  # Запихиваем в объект реплику пользователя
			user_resp.setForeground(Qt.white)
			user_resp.setFont(self.font)
			self.List.addItem(user_resp)  # Добавляем объект в интерфейс
			self.List.scrollToBottom()  # Скроллим интерфейс к самому новому

		elif value[0] == 'bot_responce':
			#output = str(Definer().define(value[1].lower())) # Запускаем обработку распознанной реплики пользователя
			output = value[1]
			if output != 'None': # Если есть реплика бота вообще
				bot_resp = QListWidgetItem()  # Делаем все тоже самое с репликой бота
				bot_resp.setTextAlignment(Qt.AlignRight)
				bot_resp.setForeground(Qt.white)
				bot_resp.setFont(self.font)
				bot_resp.setText(f"[Бот]\n{output}") # Запихиваем реплику бота
				self.List.addItem(bot_resp) # Добавляем ее в интерфейс
				self.List.scrollToBottom() # Скроллим

		elif value[0] == 'bot_exit':
			RecordThreadHandler.handler_status = False
			self.active_status = False
			self.status.setStyleSheet("background-color: rgb(209, 123, 117);") # Смена цвета кнопки

		elif value[0] == 'stop_program':
			self.close()


# Запуск собственно
if __name__ == '__main__':
	app = QApplication([])

	w = Widget()
	#350 620
	w.resize(350, 620)
	w.show()

	app.exec()
