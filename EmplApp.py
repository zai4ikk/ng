from PyQt6 import QtWidgets, QtCore, QtGui
from ui.employee import Ui_MainWindow as EmpForm
from database import Database


class EmplWindow(QtWidgets.QMainWindow, EmpForm):
    def __init__(self, user_email=None):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()

        self.pushButton_2.clicked.connect(self.logout)
        self.pushButton.clicked.connect(self.show_add_emp_dialog)
        self.home.clicked.connect(self.go_home)
        self.client.clicked.connect(self.go_client)
        self.task.clicked.connect(self.go_task)
        self.deal.clicked.connect(self.go_deal)
        self.date.clicked.connect(self.go_date)
        self.sett.clicked.connect(self.go_sett)
        self.chat.clicked.connect(self.go_chat)
        self.ana.clicked.connect(self.go_ana)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)

        self.load_data()
        self.check_user_role()

    def load_data(self):
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")

                employees = self.db.get_all_employees()

                self.tableWidget.setColumnCount(6)
                self.tableWidget.setHorizontalHeaderLabels(
                    ["Фамилия", "Имя", "Отчество", "Email", "Роль", "Должность"])
                self.tableWidget.setRowCount(len(employees))

                for row, emp in enumerate(employees):
                    for col, value in enumerate(emp):
                        item = QtWidgets.QTableWidgetItem(str(value))
                        self.tableWidget.setItem(row, col, item)

                self.tableWidget.setColumnWidth(0, 150)
                self.tableWidget.setColumnWidth(1, 150)
                self.tableWidget.setColumnWidth(2, 150)
                self.tableWidget.setColumnWidth(3, 200)
                self.tableWidget.setColumnWidth(4, 100)
                self.tableWidget.setColumnWidth(5, 150)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def check_user_role(self):
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data and user_data[5] != "админ":
                self.pushButton.hide()
        except Exception as e:
            print(f"Ошибка проверки роли: {e}")

    def show_add_emp_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Добавить сотрудника")
        dialog.setFixedSize(500, 550)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #94a5ff;
                border-radius: 5px;
                padding: 10px;
                font: 12pt "Segoe UI";
                margin-bottom: 10px;
            }
            QLabel {
                font: 500 12pt "Segoe UI";
                margin-bottom: 3px;
                margin-top: 10px;
            }
            QPushButton {
                font: 500 12pt "Segoe UI";
                background: #94a5ff;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background: #a6b4ff;
            }
            QCheckBox {
                font: 500 10pt "Segoe UI";
                margin-top: 5px;
                spacing: 5px;
            }
        """)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(container)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # Контейнер для полей ввода
        form_layout = QtWidgets.QVBoxLayout()
        form_layout.setSpacing(5)

        # Фамилия
        firstname_label = QtWidgets.QLabel("Фамилия:")
        self.firstname_edit = QtWidgets.QLineEdit()
        self.firstname_edit.setPlaceholderText("Введите фамилию")

        # Имя
        name_label = QtWidgets.QLabel("Имя:")
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя")

        # Отчество
        lastname_label = QtWidgets.QLabel("Отчество:")
        self.lastname_edit = QtWidgets.QLineEdit()
        self.lastname_edit.setPlaceholderText("Введите отчество (необязательно)")

        # Email
        email_label = QtWidgets.QLabel("Email:")
        self.email_edit = QtWidgets.QLineEdit()
        self.email_edit.setPlaceholderText("example@mail.com")

        # Пароль
        password_label = QtWidgets.QLabel("Пароль:")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("Не менее 6 символов")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # Чекбокс для показа пароля
        self.show_pass = QtWidgets.QCheckBox("Показать пароль")
        self.show_pass.stateChanged.connect(
            lambda: self.password_edit.setEchoMode(
                QtWidgets.QLineEdit.EchoMode.Normal if self.show_pass.isChecked()
                else QtWidgets.QLineEdit.EchoMode.Password
            )
        )

        # Роль
        role_label = QtWidgets.QLabel("Роль:")
        self.role_combo = QtWidgets.QComboBox()

        # Должность
        post_label = QtWidgets.QLabel("Должность:")
        self.post_combo = QtWidgets.QComboBox()

        # Заполняем комбобоксы
        self.load_combobox_data()

        # Добавляем поля в форму
        form_layout.addWidget(firstname_label)
        form_layout.addWidget(self.firstname_edit)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(lastname_label)
        form_layout.addWidget(self.lastname_edit)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_edit)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)
        form_layout.addWidget(self.show_pass)
        form_layout.addWidget(role_label)
        form_layout.addWidget(self.role_combo)
        form_layout.addWidget(post_label)
        form_layout.addWidget(self.post_combo)

        main_layout.addLayout(form_layout)

        # Кнопки
        button_box = QtWidgets.QDialogButtonBox()

        # Создаем кастомные кнопки
        add_button = QtWidgets.QPushButton("Добавить")
        add_button.clicked.connect(lambda: self.add_employee(dialog))

        back_button = QtWidgets.QPushButton("Назад")
        back_button.clicked.connect(dialog.reject)

        button_box.addButton(add_button, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(back_button, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)

        main_layout.addSpacing(20)
        main_layout.addWidget(button_box)

        scroll.setWidget(container)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        dialog_layout.addWidget(scroll)
        dialog_layout.setContentsMargins(0, 0, 0, 0)

        dialog.exec()

    def load_combobox_data(self):
        try:
            # Роли - select only the name field
            roles = self.db.get_all_roles()
            self.role_combo.addItems([role[1] for role in roles])  # Use index 1 for name

            # Должности - select only the name field
            posts = self.db.get_all_posts()
            self.post_combo.addItems([post[1] for post in posts])  # Use index 1 for name
        except Exception as e:
            print(f"Ошибка загрузки данных для комбобоксов: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных для выпадающих списков: {str(e)}")

    def add_employee(self, dialog):
        firstname = self.firstname_edit.text().strip()
        name = self.name_edit.text().strip()
        lastname = self.lastname_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        role = self.role_combo.currentText()
        post = self.post_combo.currentText()

        if not all([firstname, name, email, password]):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Обязательные поля: Фамилия, Имя, Email и Пароль")
            return

        try:
            # Получаем ID роли и должности
            role_id = self.db.get_role_id_by_name(role)
            post_id = self.db.get_post_id_by_name(post)

            if role_id is None or post_id is None:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось определить роль или должность")
                return

            # Добавляем сотрудника
            if self.db.create_employee(firstname, name, lastname, email, password, role_id, post_id):
                self.load_data()
                dialog.accept()
                QtWidgets.QMessageBox.information(self, "Успех", "Сотрудник успешно добавлен")
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить сотрудника")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось добавить сотрудника: {str(e)}")

    def go_home(self):
        from HomeApp import HomeWindow
        self.home_window = HomeWindow(self.user_email)
        self.home_window.show()
        self.close()

    def logout(self):
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def go_client(self):
        from ClientApp import ClientWindow
        self.client_window = ClientWindow(self.user_email)
        self.client_window.show()
        self.close()

    def go_task(self):
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
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
        self.db.close()
        event.accept()