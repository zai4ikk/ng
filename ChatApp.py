from PyQt6 import QtWidgets, QtCore, QtGui
from ui.chat import Ui_MainWindow as ChatForm
from database import Database


class ChatWindow(QtWidgets.QMainWindow, ChatForm):
    def __init__(self, user_email=None):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()
        self.current_chat_user_id = None

        # Инициализация UI без изменения структуры формы
        self.init_chat_ui()
        self.load_user_data()
        self.load_employees()
        self.setup_connections()

    def init_chat_ui(self):
        """Инициализация интерфейса чата внутри widget_2"""
        # Очищаем widget_2
        for i in reversed(range(self.widget_2.layout().count() if self.widget_2.layout() else 0)):
            self.widget_2.layout().itemAt(i).widget().setParent(None)

        # Устанавливаем layout для widget_2, если его нет
        if not self.widget_2.layout():
            self.widget_2.setLayout(QtWidgets.QHBoxLayout())
            self.widget_2.layout().setContentsMargins(0, 0, 0, 0)
            self.widget_2.layout().setSpacing(10)

        # Список сотрудников (левая часть)
        self.employees_list = QtWidgets.QListWidget()
        self.employees_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #94a5ff;
                border-radius: 10px;
                font: 12pt "Segoe UI";
                background: white;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:hover {
                background: #E1E5FF;
            }
            QListWidget::item:selected {
                background: #94a5ff;
                color: white;
            }
        """)

        # Область сообщений (правая часть)
        self.messages_area = QtWidgets.QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.messages_widget = QtWidgets.QWidget()
        self.messages_widget.setLayout(QtWidgets.QVBoxLayout())
        self.messages_widget.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.messages_widget.layout().setContentsMargins(10, 10, 10, 10)
        self.messages_area.setWidget(self.messages_widget)

        # Поле ввода и кнопка отправки
        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #94a5ff;
                border-radius: 10px;
                padding: 8px;
                font: 12pt "Segoe UI";
                margin: 5px;
            }
        """)

        self.send_button = QtWidgets.QPushButton("Отправить")
        self.send_button.setStyleSheet("""
            QPushButton {
                background: #94a5ff;
                border-radius: 10px;
                padding: 8px 15px;
                font: bold 12pt "Segoe UI";
                color: white;
                margin: 5px;
            }
            QPushButton:hover {
                background: #E1E5FF;
            }
            QPushButton:pressed {
                background: #717ec3;
            }
        """)

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        # Правая панель (сообщения + ввод)
        right_panel = QtWidgets.QWidget()
        right_panel.setLayout(QtWidgets.QVBoxLayout())
        right_panel.layout().setContentsMargins(0, 0, 0, 0)
        right_panel.layout().addWidget(self.messages_area)
        right_panel.layout().addLayout(input_layout)

        # Левая панель (список сотрудников)
        left_panel = QtWidgets.QWidget()
        left_panel.setLayout(QtWidgets.QVBoxLayout())
        left_panel.layout().setContentsMargins(0, 0, 0, 0)
        left_panel.layout().addWidget(QtWidgets.QLabel("Сотрудники"))
        left_panel.layout().addWidget(self.employees_list)

        # Добавляем обе панели в widget_2
        self.widget_2.layout().addWidget(left_panel)
        self.widget_2.layout().addWidget(right_panel)

        # Устанавливаем пропорции (1:3)
        self.widget_2.layout().setStretch(0, 1)
        self.widget_2.layout().setStretch(1, 3)

    def load_user_data(self):
        """Загрузка данных пользователя"""
        if self.user_email:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")

    def load_employees(self):
        """Загрузка списка сотрудников"""
        try:
            self.employees_list.clear()

            current_user = self.db.get_user_by_email(self.user_email)
            if not current_user:
                return

            employees = self.db.get_chat_users(current_user[0])

            for emp in employees:
                item = QtWidgets.QListWidgetItem(f"{emp[1]} {emp[2]} {emp[3]} ({emp[4]})")
                item.setData(QtCore.Qt.ItemDataRole.UserRole, emp[0])
                self.employees_list.addItem(item)

        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")

    def setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        self.employees_list.itemClicked.connect(self.start_chat)
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        # Подключение кнопок навигации
        self.home.clicked.connect(self.go_home)
        self.deal.clicked.connect(self.go_deal)
        self.date.clicked.connect(self.go_date)
        self.task.clicked.connect(self.go_task)
        self.client.clicked.connect(self.go_client)
        self.empl.clicked.connect(self.go_empl)
        self.ana.clicked.connect(self.go_ana)
        self.sett.clicked.connect(self.go_sett)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)
        self.pushButton_2.clicked.connect(self.logout)

    def start_chat(self, item):
        """Начало чата с выбранным сотрудником"""
        self.current_chat_user_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.load_messages(self.current_chat_user_id)

    def load_messages(self, recipient_id):
        """Загрузка сообщений с выбранным сотрудником"""
        # Очищаем предыдущие сообщения
        for i in reversed(range(self.messages_widget.layout().count())):
            widget = self.messages_widget.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            current_user = self.db.get_user_by_email(self.user_email)
            if not current_user:
                return

            messages = self.db.get_chat_messages(current_user[0], recipient_id)

            for msg in messages:
                self.add_message_to_chat(msg[0], msg[2], msg[3], current_user[0])

        except Exception as e:
            print(f"Ошибка загрузки сообщений: {e}")

    def add_message_to_chat(self, sender_id, text, timestamp, current_user_id):
        """Добавление сообщения в чат"""
        sender_name = self.get_user_name(sender_id)

        if isinstance(timestamp, QtCore.QDateTime):
            timestamp_str = timestamp.toString('dd.MM.yyyy HH:mm')
        elif hasattr(timestamp, 'strftime'):
            timestamp_str = timestamp.strftime('%d.%m.%Y %H:%M')
        else:
            timestamp_str = str(timestamp)

        message_widget = QtWidgets.QWidget()
        message_layout = QtWidgets.QVBoxLayout(message_widget)
        message_layout.setContentsMargins(5, 5, 5, 5)

        header = QtWidgets.QLabel(f"{sender_name} - {timestamp_str}")
        header.setStyleSheet("font: bold 10pt 'Segoe UI';")

        message_text = QtWidgets.QLabel(text)
        message_text.setWordWrap(True)
        message_text.setStyleSheet("""
            QLabel {
                background: #E1E5FF;
                border-radius: 10px;
                padding: 8px;
                margin: 2px;
            }
        """)

        if sender_id == current_user_id:
            message_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            message_text.setStyleSheet("""
                QLabel {
                    background: #94a5ff;
                    color: white;
                    border-radius: 10px;
                    padding: 8px;
                    margin: 2px;
                }
            """)
        else:
            message_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        message_layout.addWidget(header)
        message_layout.addWidget(message_text)

        self.messages_widget.layout().addWidget(message_widget)

        # Автопрокрутка вниз
        scroll_bar = self.messages_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def get_user_name(self, user_id):
        """Получение имени пользователя по ID"""
        try:
            sql = "SELECT firstname, name, lastname FROM userr WHERE iduser = %s"
            self.db.cursor.execute(sql, (user_id,))
            user = self.db.cursor.fetchone()
            if user:
                return f"{user[0]} {user[1]} {user[2]}"
            return "Неизвестный"
        except Exception as e:
            print(f"Ошибка получения имени пользователя: {e}")
            return "Неизвестный"

    def send_message(self):
        """Отправка сообщения"""
        if not self.current_chat_user_id:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для переписки")
            return

        message_text = self.message_input.text().strip()
        if not message_text:
            return

        try:
            current_user = self.db.get_user_by_email(self.user_email)
            if not current_user:
                return

            self.db.send_message(current_user[0], self.current_chat_user_id, message_text)

            current_time = QtCore.QDateTime.currentDateTime().toPyDateTime()
            self.add_message_to_chat(current_user[0], message_text, current_time, current_user[0])

            self.message_input.clear()

        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось отправить сообщение")

    # Методы навигации
    def go_home(self):
        from HomeApp import HomeWindow
        self.home_window = HomeWindow(self.user_email)
        self.home_window.show()
        self.close()

    def go_deal(self):
        from DealApp import DealWindow
        self.deal_window = DealWindow(self.user_email)
        self.deal_window.show()
        self.close()

    def go_date(self):
        from DateApp import DateWindow
        self.date_window = DateWindow(self.user_email)
        self.date_window.show()
        self.close()

    def go_task(self):
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
        self.close()

    def go_client(self):
        from ClientApp import ClientWindow
        self.client_window = ClientWindow(self.user_email)
        self.client_window.show()
        self.close()

    def go_empl(self):
        from EmplApp import EmplWindow
        self.empl_window = EmplWindow(self.user_email)
        self.empl_window.show()
        self.close()

    def go_ana(self):
        from AnApp import AnWindow
        self.ana_window = AnWindow(self.user_email)
        self.ana_window.show()
        self.close()

    def go_sett(self):
        from SetApp import SetWindow
        self.set_window = SetWindow(self.user_email)
        self.set_window.show()
        self.close()

    def show_notifications(self):
        from NotificationApp import NotificationWindow
        """Показать уведомления"""
        self.notification_window = NotificationWindow(self.user_email)
        self.notification_window.exec()

    def show_help(self):
        from HelpApp import HelpWindow
        """Показать справку"""
        self.help_window = HelpWindow()
        self.help_window.exec()

    def logout(self):
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.db.close()
        event.accept()

