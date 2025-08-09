from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt


class NotificationWindow(QtWidgets.QDialog):
    def __init__(self, user_email, parent=None):
        super().__init__(parent)
        self.user_email = user_email
        self.setWindowTitle("Уведомления")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(500, 400)

        # Установка иконки и фона
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/nglogo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setStyleSheet("background: url(res/gradient.png);")

        # Инициализация базы данных
        from database import Database
        self.db = Database()

        self.init_ui()
        self.load_notifications()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Ваши уведомления")
        self.title_label.setStyleSheet("font: bold 16pt 'Nirmala UI'; color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Кнопка обновления
        self.refresh_btn = QtWidgets.QPushButton("Обновить")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                font: 625 14pt "Segoe UI";
                background: #94a5ff;
                border-radius: 20px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background:#E1E5FF;
            }
            QPushButton:pressed {
                background: #717ec3;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_notifications)
        self.layout.addWidget(self.refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Прокручиваемая область для уведомлений
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setStyleSheet("background: white; border-radius: 20px;")
        self.layout.addWidget(self.scroll_area)

        # Кнопка закрытия
        self.close_btn = QtWidgets.QPushButton("Закрыть")
        self.close_btn.setStyleSheet("""
            QPushButton {
                font: 625 14pt "Segoe UI";
                background: #94a5ff;
                border-radius: 20px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background:#E1E5FF;
            }
            QPushButton:pressed {
                background: #717ec3;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn)

    def load_notifications(self):
        """Загрузка уведомлений из базы данных"""
        # Очищаем старые уведомления
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        try:
            # Получаем данные пользователя
            user_data = self.db.get_user_by_email(self.user_email)
            if not user_data:
                return

            user_id = user_data[0]

            # Получаем задачи, которые скоро истекут (в течение 24 часов)
            urgent_tasks = self.db.get_overdue_tasks(user_id)
            today_tasks = self.db.get_today_tasks(user_id)

            # Добавляем уведомления о задачах
            if urgent_tasks:
                self.add_notification_card(
                    "Срочные задачи!",
                    f"У вас {len(urgent_tasks)} просроченных задач",
                    "high"
                )

            if today_tasks:
                self.add_notification_card(
                    "Задачи на сегодня",
                    f"У вас {len(today_tasks)} задач, которые нужно выполнить сегодня",
                    "medium"
                )

            # Получаем статистику по сделкам
            deals_stats = self.db.get_deals_summary()
            if deals_stats and deals_stats[1] > 0:  # Новые сделки
                self.add_notification_card(
                    "Новые сделки",
                    f"В системе {deals_stats[1]} новых сделок, требующих обработки",
                    "medium"
                )

            # Если уведомлений нет, показываем сообщение
            if self.scroll_layout.count() == 0:
                no_notif_label = QtWidgets.QLabel("Новых уведомлений нет")
                no_notif_label.setStyleSheet("font: 12pt 'Nirmala UI'; color: gray;")
                no_notif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scroll_layout.addWidget(no_notif_label)

        except Exception as e:
            print(f"Ошибка загрузки уведомлений: {e}")
            error_label = QtWidgets.QLabel("Не удалось загрузить уведомления")
            error_label.setStyleSheet("font: 12pt 'Nirmala UI'; color: red;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(error_label)

    def add_notification_card(self, title, message, priority="low"):
        """Добавление карточки уведомления"""
        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 5px;
            }
        """)

        # Устанавливаем цвет границы в зависимости от приоритета
        if priority == "high":
            card.setStyleSheet(card.styleSheet() + "border-left: 5px solid #f44336;")
        elif priority == "medium":
            card.setStyleSheet(card.styleSheet() + "border-left: 5px solid #ff9800;")
        else:
            card.setStyleSheet(card.styleSheet() + "border-left: 5px solid #4caf50;")

        layout = QtWidgets.QVBoxLayout(card)

        # Заголовок уведомления
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font: bold 12pt 'Nirmala UI';")
        layout.addWidget(title_label)

        # Текст уведомления
        message_label = QtWidgets.QLabel(message)
        message_label.setStyleSheet("font: 10pt 'Nirmala UI';")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Время уведомления (текущее)
        time_label = QtWidgets.QLabel("Только что")
        time_label.setStyleSheet("font: 8pt 'Nirmala UI'; color: gray;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(time_label)

        self.scroll_layout.addWidget(card)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.db.close()
        event.accept()