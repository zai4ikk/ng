import sys
import os
import json
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox
from ui.recovery import Ui_MainWindow as RecoveryForm
from database import Database
import smtplib
from email.mime.text import MIMEText
import secrets
import string


class RecoveryWindow(QtWidgets.QMainWindow, RecoveryForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.db = Database()

        # Подключаем кнопки
        self.pushButton_3.clicked.connect(self.recover_password)
        self.pushButton_4.clicked.connect(self.cancel_recovery)

        # Настройки SMTP для Mail.ru по умолчанию
        self.default_smtp_settings = {
            "smtp_server": "smtp.mail.ru",
            "smtp_port": 465,
            "smtp_email": "",
            "smtp_password": "",
            "smtp_ssl": True
        }

        self.config_file = "smtp_config.json"
        self.smtp_settings = self.load_smtp_settings()

        # Если нет настроек, показать диалог настройки
        if not self.smtp_settings:
            self.show_smtp_config_dialog()

    def load_smtp_settings(self):
        """Загрузка SMTP настроек из файла конфигурации"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Проверяем наличие всех необходимых полей
                    if all(key in settings for key in self.default_smtp_settings):
                        return settings
            except Exception as e:
                print(f"Ошибка чтения конфигурации: {e}")
        return None

    def save_smtp_settings(self, settings):
        """Сохранение SMTP настроек в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False

    def show_smtp_config_dialog(self):
        """Диалоговое окно для настройки SMTP"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Настройка почты Mail.ru")
        dialog.setFixedSize(450, 350)

        layout = QtWidgets.QVBoxLayout()

        # Информационное сообщение
        info_label = QtWidgets.QLabel(
            "Для отправки писем с восстановлением пароля\n"
            "необходимо настроить SMTP сервер Mail.ru.\n\n"
            "Убедитесь, что в настройках почты Mail.ru:\n"
            "1. Включен IMAP/SMTP доступ\n"
            "2. Для 2FA создан пароль приложения"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form_layout = QtWidgets.QFormLayout()

        # Поля для ввода настроек
        self.smtp_server_edit = QtWidgets.QLineEdit(self.default_smtp_settings["smtp_server"])
        form_layout.addRow("SMTP сервер:", self.smtp_server_edit)

        self.smtp_port_edit = QtWidgets.QLineEdit(str(self.default_smtp_settings["smtp_port"]))
        form_layout.addRow("SMTP порт:", self.smtp_port_edit)

        self.smtp_email_edit = QtWidgets.QLineEdit()
        self.smtp_email_edit.setPlaceholderText("example@mail.ru")
        form_layout.addRow("Email Mail.ru:", self.smtp_email_edit)

        self.smtp_password_edit = QtWidgets.QLineEdit()
        self.smtp_password_edit.setPlaceholderText("Пароль или пароль приложения")
        self.smtp_password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль:", self.smtp_password_edit)

        self.ssl_checkbox = QtWidgets.QCheckBox("Использовать SSL")
        self.ssl_checkbox.setChecked(True)
        form_layout.addRow(self.ssl_checkbox)

        layout.addLayout(form_layout)

        # Кнопка проверки подключения
        test_btn = QtWidgets.QPushButton("Проверить подключение")
        test_btn.clicked.connect(self.test_smtp_connection)
        layout.addWidget(test_btn)

        # Кнопки OK/Cancel
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda: self.save_smtp_config(dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def test_smtp_connection(self):
        """Проверка подключения к SMTP серверу Mail.ru"""
        server = self.smtp_server_edit.text().strip()
        port = self.smtp_port_edit.text().strip()
        email = self.smtp_email_edit.text().strip()
        password = self.smtp_password_edit.text().strip()
        use_ssl = self.ssl_checkbox.isChecked()

        if not all([server, port, email, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return False

        try:
            if use_ssl:
                # Более детальная диагностика для SSL
                smtp = smtplib.SMTP_SSL(server, int(port))
                smtp.set_debuglevel(1)  # Включаем вывод отладочной информации
                smtp.login(email, password)
                smtp.quit()
            else:
                # Альтернативный вариант с TLS
                smtp = smtplib.SMTP(server, int(port))
                smtp.set_debuglevel(1)
                smtp.starttls()
                smtp.login(email, password)
                smtp.quit()

            QMessageBox.information(self, "Успех", "Подключение к SMTP серверу Mail.ru успешно!")
            return True
        except smtplib.SMTPAuthenticationError as e:
            error_msg = (
                "Ошибка аутентификации (535).\n\n"
                "Точные причины:\n"
                f"1. Код ошибки: {e.smtp_code}\n"
                f"2. Сообщение сервера: {e.smtp_error.decode()}\n\n"
                "Проверьте:\n"
                "- Правильность email и пароля\n"
                "- Включен ли IMAP/SMTP в настройках почты\n"
                "- Используете ли вы пароль приложения для 2FA"
            )
            print(e)
            QMessageBox.critical(self, "Ошибка аутентификации", error_msg)
        except Exception as e:
            error_msg = (
                f"Полная ошибка:\n{str(e)}\n\n"
                "Дополнительные проверки:\n"
                "1. Попробуйте порт 587 с TLS вместо 465 с SSL\n"
                "2. Проверьте интернет-соединение\n"
                "3. Временно отключите антивирус/файервол"
            )
            QMessageBox.critical(self, "Ошибка подключения", error_msg)

        return False

    def save_smtp_config(self, dialog):
        """Сохранение SMTP конфигурации"""
        if self.test_smtp_connection():
            self.smtp_settings = {
                "smtp_server": self.smtp_server_edit.text().strip(),
                "smtp_port": int(self.smtp_port_edit.text().strip()),
                "smtp_email": self.smtp_email_edit.text().strip(),
                "smtp_password": self.smtp_password_edit.text().strip(),
                "smtp_ssl": self.ssl_checkbox.isChecked()
            }
            if self.save_smtp_settings(self.smtp_settings):
                dialog.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки")

    def generate_random_password(self, length=12):
        """Генерация случайного пароля"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Убедимся, что пароль содержит хотя бы одну цифру и один спецсимвол
            if (any(c.isdigit() for c in password)) and (any(not c.isalnum() for c in password)):
                return password

    def send_password_email(self, recipient_email, new_password):
        """Отправка нового пароля на email через Mail.ru"""
        if not self.smtp_settings:
            QMessageBox.warning(self, "Ошибка", "SMTP настройки не заданы")
            return False

        try:
            # Создаем сообщение
            msg = MIMEText(
                f"Здравствуйте!\n\n"
                f"Вы запросили восстановление пароля для CRM системы.\n\n"
                f"Ваш новый пароль: {new_password}\n\n"
                f"Рекомендуем сменить этот пароль после входа в систему.\n\n"
                f"Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.\n\n"
                f"С уважением,\n"
                f"CRM система",
                'plain', 'utf-8'
            )

            msg['Subject'] = 'Восстановление пароля CRM системы'
            msg['From'] = self.smtp_settings['smtp_email']
            msg['To'] = recipient_email

            # Отправляем письмо
            if self.smtp_settings.get('smtp_ssl', True):
                # Используем SMTP_SSL для Mail.ru
                with smtplib.SMTP_SSL(
                    self.smtp_settings['smtp_server'],
                    self.smtp_settings['smtp_port']
                ) as server:
                    server.login(
                        self.smtp_settings['smtp_email'],
                        self.smtp_settings['smtp_password']
                    )
                    server.send_message(msg)
            else:
                # Альтернативный вариант с TLS
                with smtplib.SMTP(
                    self.smtp_settings['smtp_server'],
                    self.smtp_settings['smtp_port']
                ) as server:
                    server.starttls()
                    server.login(
                        self.smtp_settings['smtp_email'],
                        self.smtp_settings['smtp_password']
                    )
                    server.send_message(msg)

            return True
        except smtplib.SMTPException as e:
            error_msg = f"Ошибка при отправке письма:\n{str(e)}"
            if "authentication failed" in str(e).lower():
                error_msg += "\n\nПроверьте правильность email и пароля в SMTP настройках"
            QMessageBox.critical(self, "Ошибка отправки", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка при отправке письма:\n{str(e)}")

        return False

    def update_user_password(self, email, new_password):
        """Обновление пароля пользователя в базе данных"""
        try:
            # Используем триггер для автоматического хеширования пароля
            sql = "UPDATE userr SET password = %s WHERE email = %s"
            self.db.cursor.execute(sql, (new_password, email))
            self.db.connector.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось обновить пароль:\n{str(e)}")
            return False

    def recover_password(self):
        """Обработка восстановления пароля"""
        email = self.lineEdit.text().strip()

        if not email:
            QMessageBox.warning(self, "Ошибка", "Введите email")
            return

        # Проверяем существование пользователя
        user_data = self.db.get_user_by_email(email)
        if not user_data:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким email не найден")
            return

        # Генерируем новый пароль
        new_password = self.generate_random_password()

        # Отправляем email с новым паролем
        if self.send_password_email(email, new_password):
            # Обновляем пароль в базе данных
            if self.update_user_password(email, new_password):
                QMessageBox.information(
                    self,
                    "Успешно",
                    "Новый пароль был отправлен на вашу почту.\n"
                    "Проверьте папку 'Входящие' и 'Спам'.\n\n"
                    "Рекомендуем сменить пароль после входа в систему."
                )
                self.close()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Письмо было отправлено, но не удалось обновить пароль в системе.\n"
                    "Обратитесь к администратору."
                )

    def cancel_recovery(self):
        """Отмена восстановления пароля"""
        from LoginApp import Authorization
        self.login_window = Authorization()
        self.login_window.show()
        self.close()
