from PyQt6 import QtWidgets, QtCore, QtGui
from datetime import datetime
from ui.tasks import Ui_MainWindow as TaskForm
from database import Database



class TaskWindow(QtWidgets.QMainWindow, TaskForm):
    def __init__(self, user_email=None):
        super().__init__()
        try:
            self.setupUi(self)
            self.user_email = user_email
            self.db = Database()

            # Инициализация таблиц
            self.overdue_table = None
            self.today_table = None
            self.future_table = None

            # Настройка интерфейса
            self.setup_ui()

            # Загрузка данных
            self.load_data()
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Ошибка инициализации окна: {str(e)}")
            raise

    def setup_ui(self):
        """Настройка интерфейса"""
        try:
            # Подключение кнопок
            self.pushButton_2.clicked.connect(self.logout)
            self.pushButton.clicked.connect(self.show_add_task_dialog)
            self.home_2.clicked.connect(self.go_home)
            self.client_2.clicked.connect(self.go_client)
            self.empl_2.clicked.connect(self.go_empl)
            self.deal_2.clicked.connect(self.go_deal)
            self.date_2.clicked.connect(self.go_date)
            self.sett_2.clicked.connect(self.go_sett)
            self.chat_2.clicked.connect(self.go_chat)
            self.ana_2.clicked.connect(self.go_ana)
            self.notification_2.clicked.connect(self.show_notifications)
            self.help_2.clicked.connect(self.show_help)

            # Инициализация таблиц с новыми настройками
            self.overdue_table = self.create_table()
            self.today_table = self.create_table()
            self.future_table = self.create_table()

            # Добавление таблиц в контейнеры
            self.add_table_to_container(self.widget_2, self.overdue_table)
            self.add_table_to_container(self.widget_4, self.today_table)
            self.add_table_to_container(self.widget_6, self.future_table)

            # Установка текущей даты
            if hasattr(self, 'datenow'):
                today = datetime.now().strftime("%d.%m.%Y")
                self.datenow.setText(today)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка настройки интерфейса: {str(e)}")
            raise

    def create_table(self):
        """Создание и настройка таблицы задач"""
        table = QtWidgets.QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Тип", "Описание", "От кого", "Срок", "Действие"])

        # Настройка поведения столбцов
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setWordWrap(True)
        table.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)

        # Стилизация таблицы
        table.setStyleSheet("""
            QTableWidget {
                font: 12pt "Segoe UI";
                border: 1px solid #d6d6d6;
                gridline-color: #d6d6d6;
                border-radius: 0px;
            }
            QHeaderView::section {
                background-color: #94a5ff;
                color: white;
                padding: 8px;
                font: bold 12pt "Segoe UI";
                border: 1px solid #7a8eff;
                border-radius: 0px;
            }
            QTableWidget::item {
                padding: 8px;
                border-right: 1px solid #d6d6d6;
                border-bottom: 1px solid #d6d6d6;
            }
            QTableWidget::item:selected {
                background-color: #94a5ff;
                color: white;
            }
            QTableCornerButton::section {
                background-color: #94a5ff;
                border: 1px solid #7a8eff;
                border-radius: 0px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 2px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        table.verticalHeader().setDefaultSectionSize(60)
        return table

    def add_table_to_container(self, container, table):
        """Добавление таблицы в контейнер"""
        if container.layout() is None:
            layout = QtWidgets.QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        container.layout().addWidget(table)
        container.setStyleSheet("background-color: transparent; border: none; border-radius: 0px;")

    def load_data(self):
        """Загрузка данных о пользователе и задачах"""
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")
                self.load_user_tasks(user_data[0])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def load_user_tasks(self, user_id):
        """Загрузка задач пользователя по категориям"""
        try:
            # Загрузка задач из базы данных
            overdue_tasks = self.db.get_overdue_tasks(user_id)
            today_tasks = self.db.get_today_tasks(user_id)
            future_tasks = self.db.get_future_tasks(user_id)

            # Заполнение таблиц
            self.fill_table(self.overdue_table, overdue_tasks)
            self.fill_table(self.today_table, today_tasks)
            self.fill_table(self.future_table, future_tasks)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки задач: {str(e)}")

    def fill_table(self, table, tasks):
        """Заполнение таблицы задачами"""
        try:
            table.setRowCount(len(tasks))

            for row, task in enumerate(tasks):
                task_id = task[0]
                for col, value in enumerate(task[1:]):
                    item = QtWidgets.QTableWidgetItem(str(value) if value else "")
                    item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)

                    if col == 1:  # Столбец с описанием
                        item.setToolTip(str(value))

                    if col == 3 and value:  # Столбец с датой
                        if isinstance(value, datetime):
                            item.setText(value.strftime("%d.%m.%Y %H:%M"))
                            if value < datetime.now():
                                item.setBackground(QtGui.QColor(255, 230, 230))
                                item.setForeground(QtGui.QColor(200, 0, 0))
                        else:
                            item.setText(str(value))

                    table.setItem(row, col, item)

                # Добавляем кнопку выполнения
                self.add_complete_button(table, row, task_id)
                table.resizeRowToContents(row)

            table.resizeColumnsToContents()
            table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка заполнения таблицы: {str(e)}")

    def add_complete_button(self, table, row, task_id):
        """Добавление кнопки выполнения задачи"""
        btn = QtWidgets.QPushButton("Выполнить")
        btn.clicked.connect(lambda: self.complete_task(task_id))
        table.setCellWidget(row, 4, btn)

    def complete_task(self, task_id):
        """Отметка задачи как выполненной"""
        try:
            # Создаем кастомное сообщение с кнопками Да/Нет
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle('Подтверждение')
            msg_box.setText('Вы уверены, что хотите отметить задачу как выполненную?')
            msg_box.setIcon(QtWidgets.QMessageBox.Icon.Question)

            # Создаем и добавляем кнопки
            yes_button = msg_box.addButton("Да", QtWidgets.QMessageBox.ButtonRole.YesRole)
            no_button = msg_box.addButton("Нет", QtWidgets.QMessageBox.ButtonRole.NoRole)

            # Показываем диалог
            msg_box.exec()

            if msg_box.clickedButton() == yes_button:
                if self.db.complete_task(task_id):
                    self.load_data()
                    QtWidgets.QMessageBox.information(self, "Успех", "Задача отмечена как выполненная")
                else:
                    QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось обновить статус задачи")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить задачу: {str(e)}")

    def show_add_task_dialog(self):
        """Диалог добавления новой задачи"""
        try:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Новая задача")
            dialog.setFixedSize(500, 500)

            # Элементы формы
            type_label = QtWidgets.QLabel("Тип задачи:")
            self.type_combo = QtWidgets.QComboBox()

            desc_label = QtWidgets.QLabel("Описание:")
            self.desc_edit = QtWidgets.QTextEdit()
            self.desc_edit.setMaximumHeight(100)

            recipient_label = QtWidgets.QLabel("Назначить сотруднику:")
            self.recipient_combo = QtWidgets.QComboBox()

            deadline_label = QtWidgets.QLabel("Срок выполнения:")
            self.deadline_edit = QtWidgets.QDateTimeEdit()
            self.deadline_edit.setDateTime(QtCore.QDateTime.currentDateTime().addDays(1))
            self.deadline_edit.setCalendarPopup(True)
            self.deadline_edit.setDisplayFormat("dd.MM.yyyy HH:mm")

            # Кнопки
            button_box = QtWidgets.QDialogButtonBox()
            add_button = QtWidgets.QPushButton("Добавить")
            back_button = QtWidgets.QPushButton("Отмена")

            # Layout
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.addWidget(type_label)
            layout.addWidget(self.type_combo)
            layout.addWidget(desc_label)
            layout.addWidget(self.desc_edit)
            layout.addWidget(recipient_label)
            layout.addWidget(self.recipient_combo)
            layout.addWidget(deadline_label)
            layout.addWidget(self.deadline_edit)

            button_box.addButton(add_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
            button_box.addButton(back_button, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
            layout.addWidget(button_box)

            # Подключение сигналов
            add_button.clicked.connect(lambda: self.add_task(dialog))
            back_button.clicked.connect(dialog.reject)

            # Загрузка данных
            self.load_task_types()
            self.load_recipients()

            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка создания диалога: {str(e)}")

    def load_task_types(self):
        """Загрузка типов задач"""
        try:
            task_types = self.db.get_task_types()
            self.type_combo.clear()
            for task_type in task_types:
                self.type_combo.addItem(task_type[1], task_type[0])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки типов задач: {str(e)}")

    def load_recipients(self):
        """Загрузка списка сотрудников"""
        try:
            recipients = self.db.get_other_users(self.user_email)
            self.recipient_combo.clear()
            for recipient in recipients:
                self.recipient_combo.addItem(recipient[1], recipient[0])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки получателей: {str(e)}")

    def add_task(self, dialog):
        """Добавление новой задачи"""
        try:
            task_type_id = self.type_combo.currentData()
            description = self.desc_edit.toPlainText().strip()
            recipient_id = self.recipient_combo.currentData()
            deadline = self.deadline_edit.dateTime().toPyDateTime()

            if not description:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите описание задачи")
                return

            # Получаем ID отправителя
            sender_id = self.db.get_user_by_email(self.user_email)[0]

            # Добавляем задачу
            if self.db.create_task(task_type_id, description, sender_id, recipient_id, deadline):
                # Обновляем список задач
                self.load_data()
                dialog.accept()
                QtWidgets.QMessageBox.information(self, "Успех", "Задача успешно добавлена")
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить задачу")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось добавить задачу: {str(e)}")

    def go_home(self):
        """Возврат на главное окно"""
        try:
            from HomeApp import HomeWindow
            self.home_window = HomeWindow(self.user_email)
            self.home_window.show()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка перехода на главное окно: {str(e)}")

    def logout(self):
        """Выход из системы"""
        try:
            from LoginApp import Authorization
            self.auth_window = Authorization()
            self.auth_window.show()
            self.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка выхода из системы: {str(e)}")

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
        try:
            self.db.close()
            event.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка закрытия окна: {str(e)}")
            event.accept()


