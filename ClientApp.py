from PyQt6 import QtWidgets, QtCore, QtGui
from ui.organization import Ui_MainWindow as OrgForm
from database import Database


class ClientWindow(QtWidgets.QMainWindow, OrgForm):
    def __init__(self, user_email=None):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()

        self.pushButton_2.clicked.connect(self.logout)
        self.pushButton.clicked.connect(self.show_add_org_dialog)
        self.home.clicked.connect(self.go_home)
        self.empl.clicked.connect(self.go_empl)
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

                organizations = self.db.get_all_organizations()

                self.tableWidget.setColumnCount(3)
                self.tableWidget.setHorizontalHeaderLabels(["Название", "ИНН", "КПП"])
                self.tableWidget.setRowCount(len(organizations))

                for row, org in enumerate(organizations):
                    for col, value in enumerate(org[1:4]):  # Берем name, inn, kpp
                        item = QtWidgets.QTableWidgetItem(str(value))
                        self.tableWidget.setItem(row, col, item)

                self.tableWidget.setColumnWidth(0, 150)
                self.tableWidget.setColumnWidth(1, 150)
                self.tableWidget.setColumnWidth(2, 150)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def check_user_role(self):
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data and user_data[5] != "админ":
                self.pushButton.hide()
        except Exception as e:
            print(f"Ошибка проверки роли: {e}")

    def show_add_org_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Добавить организацию")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLineEdit {
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

        # Название
        name_label = QtWidgets.QLabel("Название организации:")
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Введите полное название организации")

        # ИНН
        inn_label = QtWidgets.QLabel("ИНН:")
        self.inn_edit = QtWidgets.QLineEdit()
        self.inn_edit.setPlaceholderText("10 или 12 цифр")
        self.inn_edit.setValidator(QtGui.QIntValidator())
        self.inn_edit.setMaxLength(12)

        # КПП
        kpp_label = QtWidgets.QLabel("КПП:")
        self.kpp_edit = QtWidgets.QLineEdit()
        self.kpp_edit.setPlaceholderText("9 цифр")
        self.kpp_edit.setValidator(QtGui.QIntValidator())
        self.kpp_edit.setMaxLength(9)

        # Добавляем поля в форму
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(inn_label)
        form_layout.addWidget(self.inn_edit)
        form_layout.addWidget(kpp_label)
        form_layout.addWidget(self.kpp_edit)

        main_layout.addLayout(form_layout)

        # Кнопки
        button_box = QtWidgets.QDialogButtonBox()

        # Создаем кастомные кнопки
        add_button = QtWidgets.QPushButton("Добавить")
        add_button.clicked.connect(lambda: self.add_organization(dialog))

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

    def add_organization(self, dialog):
        name = self.name_edit.text().strip()
        inn = self.inn_edit.text().strip()
        kpp = self.kpp_edit.text().strip()

        if not name or not inn or not kpp:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
            return

        try:
            if self.db.create_organization(name, inn, kpp):
                self.load_data()
                dialog.accept()
                QtWidgets.QMessageBox.information(self, "Успех", "Организация успешно добавлена")
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить организацию")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось добавить организацию: {str(e)}")

    def logout(self):
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def go_home(self):
        from HomeApp import HomeWindow
        self.home_window = HomeWindow(self.user_email)
        self.home_window.show()
        self.close()

    def go_task(self):
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
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
        self.db.close()
        event.accept()