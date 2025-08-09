import sys
from PyQt6 import QtWidgets, QtCore, QtGui, QtPrintSupport
from ui.ana import Ui_MainWindow as AnaForm
from database import Database
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class AnWindow(QtWidgets.QMainWindow, AnaForm):
    def __init__(self, user_email):
        super().__init__()
        self.setupUi(self)
        self.user_email = user_email
        self.db = Database()

        # Добавляем необходимые виджеты для аналитики
        self.setup_analytics_widgets()
        self.load_user_data()
        self.setup_connections()

    def setup_analytics_widgets(self):
        """Добавляем виджеты для аналитики на форму"""
        # Создаем вкладки для аналитики
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 120, 931, 311))
        self.tabWidget.setStyleSheet("background: white; border-radius: 15px;")

        # Вкладка со сделками
        self.tab_deals = QtWidgets.QWidget()
        self.tab_deals.setObjectName("tab_deals")
        self.tabWidget.addTab(self.tab_deals, "Сделки")

        # Вкладка с задачами
        self.tab_tasks = QtWidgets.QWidget()
        self.tab_tasks.setObjectName("tab_tasks")
        self.tabWidget.addTab(self.tab_tasks, "Задачи")

        # Создаем таблицы и графики для вкладки сделок
        self.setup_deals_tab()

        # Создаем таблицы и графики для вкладки задач
        self.setup_tasks_tab()

        # Добавляем кнопки для экспорта (расположены слева, в 2 ряда)
        self.setup_export_buttons()

    def setup_deals_tab(self):
        """Настройка вкладки со сделками"""
        layout = QtWidgets.QVBoxLayout(self.tab_deals)

        # Таблица статистики сделок
        self.table_deals = QtWidgets.QTableWidget()
        self.table_deals.setColumnCount(3)
        self.table_deals.setHorizontalHeaderLabels(["Статус", "Количество", "Сумма"])
        self.table_deals.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_deals)

        # График распределения сделок
        self.figure_deals = plt.figure()
        self.canvas_deals = FigureCanvas(self.figure_deals)
        layout.addWidget(self.canvas_deals)

    def setup_tasks_tab(self):
        """Настройка вкладки с задачами"""
        layout = QtWidgets.QVBoxLayout(self.tab_tasks)

        # Таблица статистики задач
        self.table_tasks = QtWidgets.QTableWidget()
        self.table_tasks.setColumnCount(4)
        self.table_tasks.setHorizontalHeaderLabels(["Тип", "Описание", "Отправитель", "Срок"])
        self.table_tasks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_tasks)

        # График распределения задач
        self.figure_tasks = plt.figure()
        self.canvas_tasks = FigureCanvas(self.figure_tasks)
        layout.addWidget(self.canvas_tasks)

    def setup_export_buttons(self):
        """Добавление кнопок для экспорта отчетов (2 ряда слева)"""
        self.export_widget = QtWidgets.QWidget(self.centralwidget)
        self.export_widget.setGeometry(QtCore.QRect(20, 440, 400, 80))
        self.export_widget.setStyleSheet("background: transparent;")

        # Вертикальный layout для двух рядов кнопок
        layout = QtWidgets.QVBoxLayout(self.export_widget)
        layout.setSpacing(10)

        # Первый ряд - кнопки печати
        print_layout = QtWidgets.QHBoxLayout()

        self.btn_print_deals = QtWidgets.QPushButton("Печать сделок")
        self.btn_print_deals.setFixedSize(180, 30)
        self.btn_print_deals.setStyleSheet("""
            QPushButton {
                font: 12pt "Segoe UI";
                background: #94a5ff;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #E1E5FF;
            }
        """)
        print_layout.addWidget(self.btn_print_deals)

        self.btn_print_tasks = QtWidgets.QPushButton("Печать задач")
        self.btn_print_tasks.setFixedSize(180, 30)
        self.btn_print_tasks.setStyleSheet("""
            QPushButton {
                font: 12pt "Segoe UI";
                background: #94a5ff;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #E1E5FF;
            }
        """)
        print_layout.addWidget(self.btn_print_tasks)

        layout.addLayout(print_layout)

        # Второй ряд - кнопки экспорта
        export_layout = QtWidgets.QHBoxLayout()

        self.btn_export_deals = QtWidgets.QPushButton("Экспорт сделок")
        self.btn_export_deals.setFixedSize(180, 30)
        self.btn_export_deals.setStyleSheet("""
            QPushButton {
                font: 12pt "Segoe UI";
                background: #20b06d;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #a5d6b7;
            }
        """)
        export_layout.addWidget(self.btn_export_deals)

        self.btn_export_tasks = QtWidgets.QPushButton("Экспорт задач")
        self.btn_export_tasks.setFixedSize(180, 30)
        self.btn_export_tasks.setStyleSheet("""
            QPushButton {
                font: 12pt "Segoe UI";
                background: #20b06d;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #a5d6b7;
            }
        """)
        export_layout.addWidget(self.btn_export_tasks)

        layout.addLayout(export_layout)

    def load_user_data(self):
        """Загрузка данных пользователя и аналитики"""
        try:
            user_data = self.db.get_user_by_email(self.user_email)
            if user_data:
                self.profil.setText(f"{user_data[1]} {user_data[2]}\n{user_data[6]} ({user_data[5]})")

                # Загрузка данных для аналитики
                self.load_deals_stats()
                self.load_tasks_stats()

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def load_deals_stats(self):
        """Загрузка статистики по сделкам"""
        try:
            # Очищаем таблицу
            self.table_deals.setRowCount(0)

            # Получаем данные из БД
            deals_stats = self.db.get_today_deals_stats()
            print(f"Получены данные по сделкам: {deals_stats}")  # Отладочная печать

            # Заполняем таблицу
            for row, (status, count, total) in enumerate(deals_stats):
                self.table_deals.insertRow(row)
                self.table_deals.setItem(row, 0, QtWidgets.QTableWidgetItem(status))
                self.table_deals.setItem(row, 1, QtWidgets.QTableWidgetItem(str(count)))
                self.table_deals.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{total:.2f} руб."))

            # Обновляем график
            self.update_deals_chart()

        except Exception as e:
            print(f"Ошибка загрузки статистики сделок: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка",
                                           f"Не удалось загрузить статистику сделок: {str(e)}")

    def update_deals_chart(self):
        """Обновление графика по сделкам"""
        try:
            # Очищаем график
            self.figure_deals.clear()

            # Получаем данные из БД
            data = self.db.get_deals_distribution()

            if not data:
                return

            # Подготавливаем данные для графика
            statuses = [item[0] for item in data]
            counts = [item[1] for item in data]

            # Создаем график
            ax = self.figure_deals.add_subplot(111)
            ax.bar(statuses, counts, color=['#20b06d', '#94a5ff', '#ff7e7e', '#ffcc7e'])
            ax.set_title('Распределение сделок по статусам')
            ax.set_ylabel('Количество сделок')

            # Обновляем canvas
            self.canvas_deals.draw()

        except Exception as e:
            print(f"Ошибка обновления графика сделок: {e}")

    def load_tasks_stats(self):
        """Загрузка статистики по задачам"""
        try:
            # Очищаем таблицу
            self.table_tasks.setRowCount(0)

            # Получаем данные пользователя
            user_data = self.db.get_user_by_email(self.user_email)
            if not user_data:
                return

            # Получаем задачи пользователя
            tasks = self.db.get_user_tasks(user_data[0])

            # Заполняем таблицу
            for row, (task_id, task_type, description, sender, created, deadline, completed) in enumerate(tasks):
                self.table_tasks.insertRow(row)
                self.table_tasks.setItem(row, 0, QtWidgets.QTableWidgetItem(task_type))
                self.table_tasks.setItem(row, 1, QtWidgets.QTableWidgetItem(description))
                self.table_tasks.setItem(row, 2, QtWidgets.QTableWidgetItem(sender))

                # Форматируем дату дедлайна
                deadline_date = deadline.strftime("%d.%m.%Y") if deadline else "Нет срока"
                self.table_tasks.setItem(row, 3, QtWidgets.QTableWidgetItem(deadline_date))

                # Подсветка просроченных задач
                if deadline and deadline < datetime.now() and not completed:
                    for col in range(4):
                        self.table_tasks.item(row, col).setBackground(QtGui.QColor(255, 200, 200))

            # Обновляем график
            self.update_tasks_chart()

        except Exception as e:
            print(f"Ошибка загрузки статистики задач: {e}")

    def update_tasks_chart(self):
        """Обновление графика по задачам"""
        try:
            # Очищаем график
            self.figure_tasks.clear()

            # Получаем данные пользователя
            user_data = self.db.get_user_by_email(self.user_email)
            if not user_data:
                return

            # Получаем данные из БД
            data = self.db.get_tasks_distribution(user_data[0])

            if not data:
                return

            # Подготавливаем данные для графика
            types = [item[0] for item in data]
            counts = [item[1] for item in data]

            # Создаем график
            ax = self.figure_tasks.add_subplot(111)
            ax.pie(counts, labels=types, autopct='%1.1f%%',
                   colors=['#20b06d', '#94a5ff', '#ff7e7e', '#ffcc7e'])
            ax.set_title('Распределение задач по типам')

            # Обновляем canvas
            self.canvas_tasks.draw()

        except Exception as e:
            print(f"Ошибка обновления графика задач: {e}")

    def setup_connections(self):
        """Настройка соединений для кнопок"""
        self.home.clicked.connect(self.go_home)
        self.deal.clicked.connect(self.go_deal)
        self.date.clicked.connect(self.go_date)
        self.task.clicked.connect(self.go_task)
        self.client.clicked.connect(self.go_client)
        self.empl.clicked.connect(self.go_empl)
        self.chat.clicked.connect(self.go_chat)
        self.sett.clicked.connect(self.go_sett)
        self.notification.clicked.connect(self.show_notifications)
        self.help.clicked.connect(self.show_help)
        self.pushButton_2.clicked.connect(self.logout)

        # Кнопки для работы с отчетами
        self.btn_print_deals.clicked.connect(lambda: self.print_report("deals"))
        self.btn_print_tasks.clicked.connect(lambda: self.print_report("tasks"))
        self.btn_export_deals.clicked.connect(lambda: self.export_to_pdf("deals"))
        self.btn_export_tasks.clicked.connect(lambda: self.export_to_pdf("tasks"))

    def print_report(self, report_type):
        """Печать отчета"""
        try:
            # Получаем таблицу для печати
            table = self.table_deals if report_type == "deals" else self.table_tasks

            # Проверяем, есть ли данные в таблице
            if table.rowCount() == 0:
                QtWidgets.QMessageBox.warning(self, "Предупреждение",
                                              f"Нет данных для печати отчета по {report_type}")
                return

            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.PrinterMode.HighResolution)
            page_size = QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4)
            printer.setPageSize(page_size)

            print_dialog = QtPrintSupport.QPrintDialog(printer, self)
            if print_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                document = QtGui.QTextDocument()
                html = self.generate_html_report(table, report_type)
                if html is None:  # Если нет данных, generate_html_report вернет None
                    return
                document.setHtml(html)
                document.print(printer)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить печать: {str(e)}")

    def export_to_pdf(self, report_type):
        """Экспорт отчета в PDF"""
        try:
            # Получаем таблицу для экспорта
            table = self.table_deals if report_type == "deals" else self.table_tasks

            # Проверяем, есть ли данные в таблице
            if table.rowCount() == 0:
                QtWidgets.QMessageBox.warning(self, "Предупреждение",
                                              f"Нет данных для экспорта отчета по {report_type}")
                return

            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Сохранить как PDF", "", "PDF Files (*.pdf)")

            if not file_name:
                return

            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_name)
            page_size = QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4)
            printer.setPageSize(page_size)

            document = QtGui.QTextDocument()
            html = self.generate_html_report(table, report_type)
            if html is None:  # Если нет данных, generate_html_report вернет None
                return
            document.setHtml(html)
            document.print(printer)

            QtWidgets.QMessageBox.information(self, "Успех", "Отчет успешно экспортирован в PDF")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать отчет: {str(e)}")

    def generate_html_report(self, table, report_type):
        """Генерация HTML-кода для отчета"""
        # Проверяем, есть ли данные в таблице
        if table.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "Предупреждение",
                                          f"Нет данных для отчета по {report_type}")
            return None

        # Логирование заголовков для отладки
        headers = []
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col).text()
            headers.append(header)
        print(f"Заголовки отчета: {headers}")

        # Логирование данных для отладки
        data_rows = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                text = item.text() if item else ""
                row_data.append(text)
            data_rows.append(row_data)
        print(f"Данные отчета ({len(data_rows)} строк): {data_rows}")

        html = f"""
        <html>
        <head>
        <style>
        body {{ font-family: Arial; margin: 20px; }}
        h1 {{ color: #333; text-align: center; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
        </head>
        <body>
        <h1>Отчет по {report_type}</h1>
        <p>Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        <table>
        <thead>
        <tr>
        """

        # Добавляем заголовки столбцов
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col).text()
            html += f"<th>{header}</th>"

        html += """
        </tr>
        </thead>
        <tbody>
        """

        # Добавляем данные таблицы
        for row in range(table.rowCount()):
            html += "<tr>"
            for col in range(table.columnCount()):
                item = table.item(row, col)
                text = item.text() if item else ""
                # Подсветка просроченных задач
                if report_type == "tasks" and col == 3 and item and item.background().color().name() == "#ffc8c8":
                    html += f'<td style="background-color: #ffc8c8;">{text}</td>'
                else:
                    html += f"<td>{text}</td>"
            html += "</tr>"

        html += """
        </tbody>
        </table>
        </body>
        </html>
        """

        return html

    def go_home(self):
        """Переход на главное окно"""
        from HomeApp import HomeWindow
        self.home_window = HomeWindow(self.user_email)
        self.home_window.show()
        self.close()

    def go_deal(self):
        """Переход на окно сделок"""
        from DealApp import DealWindow
        self.deal_window = DealWindow(self.user_email)
        self.deal_window.show()
        self.close()

    def go_date(self):
        """Переход на окно календаря"""
        from DateApp import DateWindow
        self.date_window = DateWindow(self.user_email)
        self.date_window.show()
        self.close()

    def go_task(self):
        """Переход на окно задач"""
        from TaskApp import TaskWindow
        self.task_window = TaskWindow(self.user_email)
        self.task_window.show()
        self.close()

    def go_client(self):
        """Переход на окно клиентов"""
        from ClientApp import ClientWindow
        self.client_window = ClientWindow(self.user_email)
        self.client_window.show()
        self.close()

    def go_empl(self):
        """Переход на окно сотрудников"""
        from EmplApp import EmplWindow
        self.empl_window = EmplWindow(self.user_email)
        self.empl_window.show()
        self.close()

    def go_chat(self):
        """Переход на окно чата"""
        from ChatApp import ChatWindow
        self.chat_window = ChatWindow(self.user_email)
        self.chat_window.show()
        self.close()

    def go_sett(self):
        """Переход на окно настроек"""
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
        """Выход из системы"""
        from LoginApp import Authorization
        self.auth_window = Authorization()
        self.auth_window.show()
        self.close()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.db.close()
        event.accept()


