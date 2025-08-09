from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt


class HelpWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(700, 600)

        # Установка иконки и фона
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/nglogo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setStyleSheet("background: url(res/gradient.png);")

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Заголовок
        self.title_label = QtWidgets.QLabel("Справочная система CRM")
        self.title_label.setStyleSheet("font: bold 16pt 'Nirmala UI'; color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Таблица с разделами справки
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #94a5ff;
                border-radius: 10px;
                background: white;
            }
            QTabBar::tab {
                background: #94a5ff;
                color: white;
                padding: 8px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #94a5ff;
            }
        """)
        self.layout.addWidget(self.tab_widget)

        # Добавляем вкладки
        self.add_general_tab()
        self.add_deals_tab()
        self.add_tasks_tab()
        self.add_contacts_tab()
        self.add_settings_tab()

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
        self.layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def add_general_tab(self):
        """Вкладка с общей информацией"""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, "Общая информация")

        layout = QtWidgets.QVBoxLayout(tab)

        # Текст справки
        help_text = """
        <h2>Добро пожаловать в CRM-систему NG-Soft!</h2>
        <p>Эта система предназначена для управления взаимоотношениями с клиентами, 
        контроля сделок и задач сотрудников.</p>

        <h3>Основные разделы:</h3>
        <ul>
            <li><b>Главная</b> - общая статистика и быстрый доступ</li>
            <li><b>Клиенты</b> - управление клиентами и контактами</li>
            <li><b>Сотрудники</b> - управление сотрудниками компании</li>
            <li><b>Задачи</b> - создание и контроль выполнения задач</li>
            <li><b>Сделки</b> - управление сделками и их статусами</li>
            <li><b>Календарь</b> - просмотр событий по датам</li>
            <li><b>Настройки</b> - настройки системы и пользователя</li>
            <li><b>Чат</b> - общение между сотрудниками</li>
            <li><b>Аналитика</b> - отчеты и статистика</li>
        </ul>

        <h3>Поддержка</h3>
        <p>По всем вопросам обращайтесь в IT-отдел: it-support@ng-soft.ru</p>
        """

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("font: 10pt 'Nirmala UI'; border: none;")
        layout.addWidget(text_edit)

    def add_deals_tab(self):
        """Вкладка с информацией о сделках"""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, "Сделки")

        layout = QtWidgets.QVBoxLayout(tab)

        help_text = """
        <h2>Управление сделками</h2>

        <h3>Создание сделки</h3>
        <p>1. Перейдите в раздел "Сделки"</p>
        <p>2. Нажмите кнопку "Добавить сделку"</p>
        <p>3. Заполните обязательные поля:</p>
        <ul>
            <li>Название сделки</li>
            <li>Тип сделки</li>
            <li>Организация</li>
            <li>Исполнитель</li>
            <li>Планируемая дата завершения</li>
        </ul>

        <h3>Статусы сделок</h3>
        <p>Сделка проходит несколько этапов:</p>
        <ol>
            <li><b>Не обработана</b> - начальный статус новой сделки</li>
            <li><b>В обработке</b> - сделка в работе у менеджера</li>
            <li><b>Выставлен счет</b> - клиенту отправлен счет</li>
            <li><b>Оплата</b> - ожидание оплаты от клиента</li>
            <li><b>В производстве</b> - выполнение работ по сделке</li>
            <li><b>Завершена</b> - сделка успешно завершена</li>
        </ol>

        <h3>Добавление счета</h3>
        <p>1. Выберите сделку в статусе "В обработке"</p>
        <p>2. Нажмите кнопку "Добавить счет"</p>
        <p>3. Укажите сумму и НДС</p>
        <p>4. Загрузите PDF-файл счета</p>
        """

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("font: 10pt 'Nirmala UI'; border: none;")
        layout.addWidget(text_edit)

    def add_tasks_tab(self):
        """Вкладка с информацией о задачах"""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, "Задачи")

        layout = QtWidgets.QVBoxLayout(tab)

        help_text = """
        <h2>Управление задачами</h2>

        <h3>Создание задачи</h3>
        <p>1. Перейдите в раздел "Задачи"</p>
        <p>2. Нажмите кнопку "Добавить задачу"</p>
        <p>3. Заполните поля:</p>
        <ul>
            <li>Тип задачи (обзвон, ВКС и т.д.)</li>
            <li>Описание задачи</li>
            <li>Исполнитель</li>
            <li>Срок выполнения</li>
        </ul>

        <h3>Типы задач</h3>
        <ul>
            <li><b>Обзвон</b> - звонок клиенту или партнеру</li>
            <li><b>ВКС</b> - видеоконференция</li>
            <li><b>Выставить счет</b> - подготовка и отправка счета</li>
        </ul>

        <h3>Отметка о выполнении</h3>
        <p>1. Найдите задачу в списке</p>
        <p>2. Нажмите кнопку "Выполнено"</p>
        <p>3. Задача переместится в раздел выполненных</p>
        """

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("font: 10pt 'Nirmala UI'; border: none;")
        layout.addWidget(text_edit)

    def add_contacts_tab(self):
        """Вкладка с информацией о контактах"""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, "Клиенты")

        layout = QtWidgets.QVBoxLayout(tab)

        help_text = """
        <h2>Управление клиентами</h2>

        <h3>Добавление организации</h3>
        <p>1. Перейдите в раздел "Клиенты"</p>
        <p>2. Нажмите кнопку "Добавить организацию"</p>
        <p>3. Заполните реквизиты:</p>
        <ul>
            <li>Название организации</li>
            <li>ИНН (10 или 12 цифр)</li>
            <li>КПП (9 цифр)</li>
        </ul>

        <h3>Добавление контакта</h3>
        <p>1. Выберите организацию</p>
        <p>2. Нажмите "Добавить контакт"</p>
        <p>3. Укажите ФИО и должность</p>
        <p>4. Добавьте контактные данные</p>
        """

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("font: 10pt 'Nirmala UI'; border: none;")
        layout.addWidget(text_edit)

    def add_settings_tab(self):
        """Вкладка с информацией о настройках"""
        tab = QtWidgets.QWidget()
        self.tab_widget.addTab(tab, "Настройки")

        layout = QtWidgets.QVBoxLayout(tab)

        help_text = """
        <h2>Настройки системы</h2>

        <h3>Изменение пароля</h3>
        <p>1. Перейдите в раздел "Настройки"</p>
        <p>2. Введите текущий пароль</p>
        <p>3. Введите новый пароль дважды</p>
        <p>4. Нажмите "Сохранить"</p>

        <h3>Настройки CRM</h3>
        <p>Доступны только администраторам:</p>
        <ul>
            <li>Добавление/удаление типов сделок</li>
            <li>Добавление/удаление статусов сделок</li>
            <li>Добавление/удаление типов задач</li>
            <li>Управление должностями</li>
            <li>Управление ролями пользователей</li>
        </ul>
        """

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        text_edit.setStyleSheet("font: 10pt 'Nirmala UI'; border: none;")
        layout.addWidget(text_edit)