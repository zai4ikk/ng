from PyQt6 import QtWidgets, QtCore
from ui.set import Ui_MainWindow as SetForm
from database import Database
import sys


class SetWindow(QtWidgets.QMainWindow, SetForm):
    def __init__(self, user_email=None):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()

        self.init_ui()
        self.load_user_data()
        self.setup_connections()

    def init_ui(self):
        """Initialize UI elements"""
        # Hide admin buttons initially
        self.hide_admin_buttons()

        # Check if user is admin and show appropriate buttons
        if self.user_email:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data and user_data[5] == 'админ':  # Check if role is admin
                self.show_admin_buttons()

    def hide_admin_buttons(self):
        """Hide admin-only buttons"""
        self.pushButton_5.hide()  # Удалить/добавить должность
        self.pushButton_6.hide()  # Удалить/добавить тип задачи
        self.pushButton_7.hide()  # Удалить/добавить статус сделки
        self.pushButton_8.hide()  # Удалить/добавить тип сделки
        self.pushButton_9.hide()  # Добавить новую роль

    def show_admin_buttons(self):
        """Show admin-only buttons"""
        self.pushButton_5.show()  # Удалить/добавить должность
        self.pushButton_6.show()  # Удалить/добавить тип задачи
        self.pushButton_7.show()  # Удалить/добавить статус сделки
        self.pushButton_8.show()  # Удалить/добавить тип сделки
        self.pushButton_9.show()  # Добавить новую роль

    def load_user_data(self):
        """Load user data to display"""
        if self.user_email:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                # Display user info
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")

    def setup_connections(self):
        """Setup button connections"""
        # Navigation buttons
        self.home.clicked.connect(self.go_home)
        self.deal.clicked.connect(self.go_deal)
        self.date.clicked.connect(self.go_date)
        self.task.clicked.connect(self.go_task)
        self.client.clicked.connect(self.go_client)
        self.empl.clicked.connect(self.go_empl)
        self.chat.clicked.connect(self.go_chat)
        self.ana.clicked.connect(self.go_ana)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)
        self.pushButton_2.clicked.connect(self.logout)

        # Personal info buttons
        self.pushButton.clicked.connect(lambda: self.change_user_info('name'))
        self.pushButton_3.clicked.connect(lambda: self.change_user_info('firstname'))
        self.pushButton_4.clicked.connect(lambda: self.change_user_info('lastname'))

        # Admin buttons
        self.pushButton_5.clicked.connect(lambda: self.manage_entity('post'))
        self.pushButton_6.clicked.connect(lambda: self.manage_entity('typetask'))
        self.pushButton_7.clicked.connect(lambda: self.manage_entity('statusdeal'))
        self.pushButton_8.clicked.connect(lambda: self.manage_entity('typedeal'))
        self.pushButton_9.clicked.connect(self.add_new_role)

    def change_user_info(self, field):
        """Change user's name, firstname or lastname"""
        if not self.user_email:
            return

        # Create custom dialog with Russian buttons
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle(f"Изменить {self.get_field_name(field)}")
        dialog.setLabelText(f"Введите новое {self.get_field_name(field)}:")
        dialog.setOkButtonText("Применить")
        dialog.setCancelButtonText("Отмена")

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted and dialog.textValue():
            text = dialog.textValue()
            try:
                user_data = self.db.get_user_by_email(self.user_email)
                if user_data:
                    if self.db.update_user_info(user_data[0], field, text):
                        # Reload user data
                        self.load_user_data()
                        QtWidgets.QMessageBox.information(
                            self,
                            "Успех",
                            f"{self.get_field_name(field).capitalize()} успешно изменено"
                        )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось изменить {self.get_field_name(field)}: {str(e)}"
                )

    def get_field_name(self, field):
        """Get Russian field name for display"""
        names = {
            'name': 'имя',
            'firstname': 'фамилию',
            'lastname': 'отчество'
        }
        return names.get(field, '')

    def manage_entity(self, entity_type):
        """Manage different entities (posts, task types, etc.)"""
        if not self.user_email:
            return

        # Get current entities
        if entity_type == 'post':
            entities = self.db.get_all_posts()
            title = "Должности"
        elif entity_type == 'typetask':
            entities = self.db.get_all_task_types()
            title = "Типы задач"
        elif entity_type == 'statusdeal':
            entities = self.db.get_all_deal_statuses()
            title = "Статусы сделок"
        elif entity_type == 'typedeal':
            entities = self.db.get_all_deal_types()
            title = "Типы сделок"
        else:
            return

        # Show dialog to manage entities
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Управление {title.lower()}")
        dialog.setMinimumSize(400, 300)

        layout = QtWidgets.QVBoxLayout(dialog)

        # List widget to display current entities
        list_widget = QtWidgets.QListWidget()
        for entity in entities:
            item = QtWidgets.QListWidgetItem(entity[1])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, entity[0])  # Store ID
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()

        # Add button
        add_btn = QtWidgets.QPushButton("Добавить")
        add_btn.clicked.connect(lambda: self.add_entity(entity_type, list_widget))
        buttons_layout.addWidget(add_btn)

        # Remove button
        remove_btn = QtWidgets.QPushButton("Удалить")
        remove_btn.clicked.connect(lambda: self.remove_entity(entity_type, list_widget))
        buttons_layout.addWidget(remove_btn)

        layout.addLayout(buttons_layout)

        dialog.exec()

    def add_entity(self, entity_type, list_widget):
        """Add new entity"""
        # Create custom dialog with Russian buttons
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Добавить")
        dialog.setLabelText("Введите название нового элемента:")
        dialog.setOkButtonText("Добавить")
        dialog.setCancelButtonText("Отмена")

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted and dialog.textValue():
            text = dialog.textValue()
            try:
                if self.db.add_entity(entity_type, text):
                    # Get the updated list
                    if entity_type == 'post':
                        entities = self.db.get_all_posts()
                    elif entity_type == 'typetask':
                        entities = self.db.get_all_task_types()
                    elif entity_type == 'statusdeal':
                        entities = self.db.get_all_deal_statuses()
                    elif entity_type == 'typedeal':
                        entities = self.db.get_all_deal_types()
                    else:
                        return

                    # Update list widget
                    list_widget.clear()
                    for entity in entities:
                        item = QtWidgets.QListWidgetItem(entity[1])
                        item.setData(QtCore.Qt.ItemDataRole.UserRole, entity[0])
                        list_widget.addItem(item)

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось добавить элемент: {str(e)}"
                )

    def remove_entity(self, entity_type, list_widget):
        """Remove selected entity"""
        selected_item = list_widget.currentItem()
        if not selected_item:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите элемент для удаления")
            return

        entity_id = selected_item.data(QtCore.Qt.ItemDataRole.UserRole)
        entity_name = selected_item.text()

        # Create custom message box with Russian buttons
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText(f"Вы уверены, что хотите удалить '{entity_name}'?")
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No
        )
        msg_box.button(QtWidgets.QMessageBox.StandardButton.Yes).setText("Да")
        msg_box.button(QtWidgets.QMessageBox.StandardButton.No).setText("Нет")

        if msg_box.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                if self.db.delete_entity(entity_type, entity_id):
                    list_widget.takeItem(list_widget.row(selected_item))
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить элемент: {str(e)}"
                )

    def add_new_role(self):
        """Add new role to the system"""
        if not self.user_email:
            return

        # Create custom dialog with Russian buttons
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Добавить роль")
        dialog.setLabelText("Введите название новой роли:")
        dialog.setOkButtonText("Добавить")
        dialog.setCancelButtonText("Отмена")

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted and dialog.textValue():
            text = dialog.textValue()
            try:
                if self.db.add_entity('role', text):
                    QtWidgets.QMessageBox.information(
                        self,
                        "Успех",
                        "Новая роль успешно добавлена"
                    )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось добавить роль: {str(e)}"
                )

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

    def logout(self):
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def closeEvent(self, event):
        """Handle window close event"""
        self.db.close()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SetWindow("i.oleg@ng-soft.ru")
    window.show()
    sys.exit(app.exec())