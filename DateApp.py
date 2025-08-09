import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from ui.date import Ui_MainWindow as DateForm
from datetime import datetime
from database import Database


class DateWindow(QtWidgets.QMainWindow, DateForm):
    def __init__(self, user_email):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.current_user = None
        self.db = Database()

        # Добавляем QLabel для отображения текущей даты (перенесено ниже меню)
        self.date_label = QtWidgets.QLabel(self.centralwidget)
        self.date_label.setGeometry(QtCore.QRect(50, 100, 611, 30))
        self.date_label.setStyleSheet("font: 14pt 'Segoe UI';")
        self.date_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.init_ui()
        self.load_user_data()
        self.load_calendar_data()

        # Подключаем кнопки
        self.pushButton_2.clicked.connect(self.logout)
        self.home.clicked.connect(self.go_home)
        self.task.clicked.connect(self.go_task)
        self.client.clicked.connect(self.go_client)
        self.empl.clicked.connect(self.go_empl)
        self.deal.clicked.connect(self.go_deal)
        self.sett.clicked.connect(self.go_sett)
        self.chat.clicked.connect(self.go_chat)
        self.ana.clicked.connect(self.go_ana)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)

        # Настройка календаря (перенесено ниже метки даты)
        self.calendarWidget.setGeometry(QtCore.QRect(50, 140, 611, 451))
        self.calendarWidget.selectionChanged.connect(self.on_date_selected)
        self.calendarWidget.setGridVisible(True)
        self.calendarWidget.setVerticalHeaderFormat(
            QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

    def init_ui(self):
        """Настройка интерфейса"""
        today = datetime.now().strftime("%d.%m.%Y")
        self.date_label.setText(f"Сегодня: {today}")
        self.pushButton_2.setText("Выйти")

        # Убедимся, что меню находится выше метки даты
        self.widget.setGeometry(QtCore.QRect(280, 20, 671, 71))
        self.date_label.raise_()

    def load_user_data(self):
        """Загрузка данных пользователя"""
        try:
            self.current_user = self.db.get_user_by_email(self.user_email)
            if self.current_user and hasattr(self, 'profil'):
                self.profil.setText(
                    f"{self.current_user[1]} {self.current_user[2]}\n"
                    f"{self.current_user[6]} ({self.current_user[5]})"
                )
        except Exception as e:
            print(f"Ошибка загрузки данных пользователя: {e}")

    def load_calendar_data(self):
        """Загрузка данных для календаря"""
        try:
            if not self.current_user:
                return

            # Получаем даты задач и сделок пользователя
            task_dates = self.db.get_user_task_dates(self.current_user[0])
            deal_dates = self.db.get_user_deal_dates(self.current_user[0])

            # Форматируем даты для выделения в календаре
            self.highlight_dates(task_dates, deal_dates)

        except Exception as e:
            print(f"Ошибка загрузки данных календаря: {e}")

    def highlight_dates(self, task_dates, deal_dates):
        """Выделение дат в календаре"""
        # Создаем форматы для разных типов событий
        task_format = QtGui.QTextCharFormat()
        task_format.setBackground(QtGui.QColor(255, 200, 200))  # Красный для задач
        task_format.setToolTip("Срок сдачи задачи")

        deal_format = QtGui.QTextCharFormat()
        deal_format.setBackground(QtGui.QColor(200, 255, 200))  # Зеленый для сделок
        deal_format.setToolTip("Срок завершения сделки")

        both_format = QtGui.QTextCharFormat()
        both_format.setBackground(QtGui.QColor(255, 255, 200))  # Желтый для обоих событий
        both_format.setToolTip("Срок сдачи задачи и завершения сделки")

        # Очищаем предыдущие выделения
        self.calendarWidget.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

        # Создаем словарь для хранения дат и их типов
        date_dict = {}

        # Добавляем даты задач
        for date in task_dates:
            qdate = QtCore.QDate(date.year, date.month, date.day)
            date_dict[qdate] = date_dict.get(qdate, 0) | 1  # 1 - задача

        # Добавляем даты сделок
        for date in deal_dates:
            qdate = QtCore.QDate(date.year, date.month, date.day)
            date_dict[qdate] = date_dict.get(qdate, 0) | 2  # 2 - сделка

        # Применяем форматирование
        for date, event_type in date_dict.items():
            if event_type == 1:  # Только задача
                self.calendarWidget.setDateTextFormat(date, task_format)
            elif event_type == 2:  # Только сделка
                self.calendarWidget.setDateTextFormat(date, deal_format)
            else:  # Оба события
                self.calendarWidget.setDateTextFormat(date, both_format)

    def on_date_selected(self):
        """Обработчик выбора даты в календаре"""
        selected_date = self.calendarWidget.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        self.date_label.setText(f"Выбрана дата: {selected_date.toString('dd.MM.yyyy')}")

        try:
            if not self.current_user:
                return

            # Получаем задачи и сделки на выбранную дату
            tasks = self.db.get_tasks_for_date(self.current_user[0], date_str)
            deals = self.db.get_deals_for_date(self.current_user[0], date_str)

            # Показываем информацию в диалоговом окне
            self.show_date_info(selected_date.toString("dd.MM.yyyy"), tasks, deals)

        except Exception as e:
            print(f"Ошибка загрузки данных для даты: {e}")

    def show_date_info(self, date_str, tasks, deals):
        """Показ информации о выбранной дате"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"События на {date_str}")
        dialog.setMinimumSize(500, 400)

        layout = QtWidgets.QVBoxLayout(dialog)
        tab_widget = QtWidgets.QTabWidget()

        # Вкладка с задачами
        tasks_tab = QtWidgets.QWidget()
        tasks_layout = QtWidgets.QVBoxLayout(tasks_tab)

        if tasks:
            for task in tasks:
                task_frame = QtWidgets.QFrame()
                task_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
                task_frame.setStyleSheet("""
                    background-color: #FFE8E8; 
                    border-radius: 5px; 
                    padding: 10px;
                    margin: 5px;
                """)

                task_vbox = QtWidgets.QVBoxLayout(task_frame)

                desc_label = QtWidgets.QLabel(f"<b>Описание:</b> {task[0]}")
                type_label = QtWidgets.QLabel(f"<b>Тип:</b> {task[1]}")
                sender_label = QtWidgets.QLabel(f"<b>От:</b> {task[2]}")

                desc_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
                type_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
                sender_label.setTextFormat(QtCore.Qt.TextFormat.RichText)

                task_vbox.addWidget(desc_label)
                task_vbox.addWidget(type_label)
                task_vbox.addWidget(sender_label)

                tasks_layout.addWidget(task_frame)
        else:
            no_tasks = QtWidgets.QLabel("Нет задач на выбранную дату")
            no_tasks.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            tasks_layout.addWidget(no_tasks)

        tab_widget.addTab(tasks_tab, f"Задачи ({len(tasks)})")

        # Вкладка со сделками
        deals_tab = QtWidgets.QWidget()
        deals_layout = QtWidgets.QVBoxLayout(deals_tab)

        if deals:
            for deal in deals:
                deal_frame = QtWidgets.QFrame()
                deal_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
                deal_frame.setStyleSheet("""
                    background-color: #E8FFE8; 
                    border-radius: 5px; 
                    padding: 10px;
                    margin: 5px;
                """)

                deal_vbox = QtWidgets.QVBoxLayout(deal_frame)

                name_label = QtWidgets.QLabel(f"<b>Сделка:</b> {deal[0]}")
                type_label = QtWidgets.QLabel(f"<b>Тип:</b> {deal[1]}")
                status_label = QtWidgets.QLabel(f"<b>Статус:</b> {deal[2]}")

                name_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
                type_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
                status_label.setTextFormat(QtCore.Qt.TextFormat.RichText)

                deal_vbox.addWidget(name_label)
                deal_vbox.addWidget(type_label)
                deal_vbox.addWidget(status_label)

                deals_layout.addWidget(deal_frame)
        else:
            no_deals = QtWidgets.QLabel("Нет сделок на выбранную дату")
            no_deals.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            deals_layout.addWidget(no_deals)

        tab_widget.addTab(deals_tab, f"Сделки ({len(deals)})")

        layout.addWidget(tab_widget)

        # Кнопка закрытия
        button_box = QtWidgets.QDialogButtonBox()
        close_btn = button_box.addButton("Закрыть", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(button_box)

        dialog.exec()

    def logout(self):
        """Выход из системы"""
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def go_home(self):
        """Переход на главный экран"""
        from HomeApp import HomeWindow
        self.home_window = HomeWindow(self.user_email)
        self.home_window.show()
        self.close()

    def go_task(self):
        """Переход к задачам"""
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
        self.close()

    def go_client(self):
        """Переход к клиентам"""
        from ClientApp import ClientWindow
        self.client_window = ClientWindow(self.user_email)
        self.client_window.show()
        self.close()

    def go_empl(self):
        """Переход к сотрудникам"""
        from EmplApp import EmplWindow
        self.empl_window = EmplWindow(self.user_email)
        self.empl_window.show()
        self.close()

    def go_deal(self):
        """Переход к сделкам"""
        from DealApp import DealWindow
        self.deal_window = DealWindow(self.user_email)
        self.deal_window.show()
        self.close()

    def go_sett(self):
        from SetApp import SetWindow
        self.set_window = SetWindow(self.user_email)
        self.set_window.show()
        self.close()

    def go_chat(self):
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


