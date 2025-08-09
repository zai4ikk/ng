from PyQt6 import QtWidgets, QtCore
from ui.home import Ui_MainWindow as HomeForm
from datetime import datetime
from database import Database


class HomeWindow(QtWidgets.QMainWindow, HomeForm):
    def __init__(self, user_email):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()

        self.init_ui()
        self.load_data()

        self.pushButton_2.clicked.connect(self.logout)
        self.client.clicked.connect(self.go_client)
        self.empl.clicked.connect(self.go_empl)
        self.task.clicked.connect(self.go_task)
        self.deal.clicked.connect(self.go_deal)
        self.date.clicked.connect(self.go_date)
        self.sett.clicked.connect(self.go_sett)
        self.chat.clicked.connect(self.go_chat)
        self.ana.clicked.connect(self.go_ana)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)


    def init_ui(self):
        """Настройка интерфейса"""
        today = datetime.now().strftime("%d.%m.%Y")
        self.datenow.setText(today)

        # Настройка layout для widget_2
        self.deals_layout = QtWidgets.QVBoxLayout(self.widget_2)
        self.deals_layout.setContentsMargins(10, 10, 10, 10)
        self.deals_layout.setSpacing(15)

        # Заголовок для виджета со сделками
        self.deals_title = QtWidgets.QLabel("Статистика сделок за сегодня")
        self.deals_title.setStyleSheet("font: bold 14pt 'Nirmala UI';")
        self.deals_layout.addWidget(self.deals_title)

        # Контейнер для карточек
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(15)
        self.deals_layout.addWidget(self.cards_container)

    def create_deal_card(self, status, count, total):
        """Создание карточки для отображения статистики сделок"""
        card = QtWidgets.QFrame()
        card.setMinimumSize(150, 120)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #20b06d;
            }
            QLabel {
                font: 12pt 'Nirmala UI';
            }
        """)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Заголовок карточки (статус)
        status_label = QtWidgets.QLabel(status)
        status_label.setStyleSheet("font: bold 12pt 'Nirmala UI'; color: #20b06d;")
        status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Количество сделок
        count_label = QtWidgets.QLabel(f"Количество: {count}")
        count_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Сумма сделок
        total_label = QtWidgets.QLabel(f"Сумма: {total:.2f} руб.")
        total_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(status_label)
        layout.addWidget(count_label)
        layout.addWidget(total_label)

        return card

    def load_data(self):
        """Загрузка данных"""
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")

                # Очищаем старые карточки
                for i in reversed(range(self.cards_layout.count())):
                    self.cards_layout.itemAt(i).widget().setParent(None)

                # Добавляем новые карточки
                deals_stats = self.db.get_today_deals_stats()
                for status, count, total in deals_stats:
                    card = self.create_deal_card(status, count, total)
                    self.cards_layout.addWidget(card)

                # Если нет сделок, показываем сообщение
                if not deals_stats:
                    no_deals_label = QtWidgets.QLabel("Сегодня сделок нет")
                    no_deals_label.setStyleSheet("font: 12pt 'Nirmala UI';")
                    self.cards_layout.addWidget(no_deals_label)

                tasks_count, urgent_count = self.db.get_user_tasks_count(user_data[0])
                self.task_do.setText(str(tasks_count))
                self.task_sos.setText(str(urgent_count))
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def logout(self):
        # Выход из системы
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def go_client(self):
        from ClientApp import ClientWindow
        self.client_window = ClientWindow(self.user_email)  # Передаем email
        self.client_window.show()
        self.close()

    def go_empl(self):
        from EmplApp import EmplWindow
        self.empl_window = EmplWindow(self.user_email)  # Передаем email
        self.empl_window.show()
        self.close()

    def go_task(self):
        # Выход из системы
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
        self.close()

    def go_deal(self):
        # Выход из системы
        from DealApp import DealWindow
        self.deal_window = DealWindow(self.user_email)
        self.deal_window.show()
        self.close()

    def go_date(self):
        # Выход из системы
        from DateApp import DateWindow
        self.date_window = DateWindow(self.user_email)
        self.date_window.show()
        self.close()

    def go_sett(self):
        from SetApp import SetWindow
        self.set_window = SetWindow(self.user_email)
        self.set_window.show()
        self.close()

    def go_chat(self):
        # Выход из системы
        from ChatApp import ChatWindow
        self.chat_window = ChatWindow(self.user_email)
        self.chat_window.show()
        self.close()

    def go_ana(self):
        from AnApp import AnWindow
        self.ana_window = AnWindow(self.user_email)
        self.ana_window.show()
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

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.db.close()
        event.accept()