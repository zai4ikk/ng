import sys
from PyQt6 import QtWidgets
from ui.auth import Ui_MainWindow as AuthForm
from database import Database


class Authorization(QtWidgets.QMainWindow, AuthForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = Database()
        self.pushButton_3.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.show_recovery_window)
        self.home_window = None  # Ссылка на главное окно
        self.recovery_window = None  # Ссылка на окно восстановления

    def login(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Email и пароль обязательны")
            return

        try:
            user_data = self.db.get_user_by_email(email)

            if not user_data:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь не найден")
                return

            if self.db.verify_password(password, user_data[4]):
                self.close()  # Скрываем окно авторизации вместо закрытия

                # Создаем главное окно если его нет
                if not self.home_window:
                    from HomeApp import HomeWindow
                    self.home_window = HomeWindow(email)

                self.home_window.show()
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный пароль")

        except Exception as err:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка системы: {str(err)}")
            print(f"Error: {err}")

    def show_recovery_window(self):
        """Показать окно восстановления пароля"""
        if not self.recovery_window:
            from RecoveryApp import RecoveryWindow
            self.recovery_window = RecoveryWindow()

        self.recovery_window.show()
        self.close()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.db.close()
        event.accept()