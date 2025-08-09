import pymysql


class Database:
    def __init__(self):
        self.connector = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="crm"
        )
        self.connector.autocommit(True)
        self.cursor = self.connector.cursor()

    """Методы для авторизации"""

    def get_user_by_email(self, email):
        """Получить пользователя по email"""
        sql = """SELECT userr.iduser, userr.firstname, userr.name, userr.lastname, 
                        userr.password, role.name as role, post.name as post
                 FROM userr 
                 JOIN role ON userr.idr = role.idrole
                 JOIN post ON userr.idp = post.idpost
                 WHERE userr.email = %s"""
        self.cursor.execute(sql, (email,))
        return self.cursor.fetchone()

    def verify_password(self, plain_password, hashed_password):
        """Проверить пароль"""
        check_sql = "SELECT SHA2(%s, 256) = %s AS password_match"
        self.cursor.execute(check_sql, (plain_password, hashed_password))
        return self.cursor.fetchone()[0]

    """Методы для главного окна"""

    def get_today_deals_stats(self):
        """Статистика сделок за сегодня"""
        sql = """SELECT statusdeal.name, COUNT(deal.iddeal), COALESCE(SUM(deal.total_price), 0)
                 FROM deal
                 JOIN statusdeal ON deal.idsd = statusdeal.idstatusdeal
                 WHERE DATE(deal.date1) = CURDATE()
                 GROUP BY statusdeal.name"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_user_tasks_count(self, user_id):
        """Количество задач пользователя"""
        # Все активные задачи
        sql_tasks = """SELECT COUNT(*) FROM task 
                      WHERE recipient = %s AND (date2 IS NULL OR date2 >= CURDATE())"""
        self.cursor.execute(sql_tasks, (user_id,))
        tasks_count = self.cursor.fetchone()[0]

        # Срочные задачи
        sql_urgent = """SELECT COUNT(*) FROM task 
                       WHERE recipient = %s AND date2 IS NOT NULL 
                       AND date2 <= DATE_ADD(CURDATE(), INTERVAL 1 DAY)"""
        self.cursor.execute(sql_urgent, (user_id,))
        urgent_count = self.cursor.fetchone()[0]

        return tasks_count, urgent_count

    """Методы для работы со сделками"""

    def get_all_deals(self):
        """Получение всех сделок с названиями типов, статусов и организаций"""
        sql = """SELECT d.iddeal, d.name, td.name as type, sd.name as status, 
                        o.name as organization, 
                        CONCAT(u.firstname, ' ', u.name, ' ', u.lastname) as executor,
                        d.date1, d.date2, d.price, d.nds, d.total_price, d.bill
                 FROM deal d
                 JOIN typedeal td ON d.idtd = td.idtypedeal
                 JOIN statusdeal sd ON d.idsd = sd.idstatusdeal
                 JOIN organization o ON d.ido = o.idorganization
                 JOIN userr u ON d.executor = u.iduser"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def create_deal(self, name, type_id, org_id, executor_id, end_date):
        """Создание новой сделки"""
        try:
            # Статус по умолчанию - "Не обработан" (id=1)
            sql = """INSERT INTO deal (name, idtd, idsd, ido, executor, date1, date2) 
                     VALUES (%s, %s, 1, %s, %s, NOW(), %s)"""
            self.cursor.execute(sql, (name, type_id, org_id, executor_id, end_date))
            self.connector.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка создания сделки: {e}")
            return False

    def get_organization_details(self, org_identifier):
        """Получение информации об организации по ID или названию"""
        try:
            if isinstance(org_identifier, int) or (isinstance(org_identifier, str) and org_identifier.isdigit()):
                # Поиск по ID
                sql = """SELECT idorganization, name, inn, kpp 
                         FROM organization 
                         WHERE idorganization = %s"""
            else:
                # Поиск по названию
                sql = """SELECT idorganization, name, inn, kpp 
                         FROM organization 
                         WHERE name LIKE %s"""

            self.cursor.execute(sql, (org_identifier,))
            result = self.cursor.fetchone()

            if not result:
                print(f"Организация {org_identifier} не найдена")
                return None

            return {
                'id': result[0],
                'name': result[1],
                'inn': result[2],
                'kpp': result[3]
            }
        except Exception as e:
            print(f"Ошибка при получении данных организации: {str(e)}")
            return None

    def update_deal_bill(self, deal_id, bill_data):
        """Обновление счета сделки"""
        try:
            sql = "UPDATE deal SET bill = %s WHERE iddeal = %s"
            self.cursor.execute(sql, (bill_data, deal_id))
            self.connector.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления счета сделки: {e}")
            return False

    def update_deal_price(self, deal_id, price, nds, total_price, status_name):
        """Обновление цены, НДС и статуса сделки"""
        try:
            # Получаем ID статуса по названию
            status_id = self.get_status_id_by_name(status_name)
            if not status_id:
                return False

            sql = """UPDATE deal 
                     SET price = %s, nds = %s, total_price = %s, idsd = %s 
                     WHERE iddeal = %s"""
            self.cursor.execute(sql, (price, nds, total_price, status_id, deal_id))
            self.connector.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления цены сделки: {e}")
            return False

    def update_deal_status(self, deal_id, status_id):
        """Обновление статуса сделки"""
        try:
            sql = "UPDATE deal SET idsd = %s WHERE iddeal = %s"
            self.cursor.execute(sql, (status_id, deal_id))
            self.connector.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления статуса сделки: {e}")
            return False

    def get_status_id_by_name(self, status_name):
        """Получение ID статуса по названию"""
        try:
            sql = "SELECT idstatusdeal FROM statusdeal WHERE name = %s"
            self.cursor.execute(sql, (status_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка получения ID статуса: {e}")
            return None

    def get_deals_by_executor(self, executor_id):
        """Получение сделок конкретного исполнителя"""
        sql = """SELECT d.iddeal, d.name, td.name as type, sd.name as status, 
                        o.name as organization, 
                        CONCAT(u.firstname, ' ', u.name, ' ', u.lastname) as executor,
                        d.date1, d.date2, d.price, d.nds, d.total_price, d.bill
                 FROM deal d
                 JOIN typedeal td ON d.idtd = td.idtypedeal
                 JOIN statusdeal sd ON d.idsd = sd.idstatusdeal
                 JOIN organization o ON d.ido = o.idorganization
                 JOIN userr u ON d.executor = u.iduser
                 WHERE d.executor = %s"""
        self.cursor.execute(sql, (executor_id,))
        return self.cursor.fetchall()

    """Методы для работы с настройками системы"""

    def get_all_deal_statuses(self):
        """Получение всех статусов сделок"""
        sql = "SELECT idstatusdeal, name FROM statusdeal ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_deal_types(self):
        """Получение всех типов сделок"""
        sql = "SELECT idtypedeal, name FROM typedeal ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_posts(self):
        """Получение всех должностей"""
        sql = "SELECT idpost, name FROM post ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_task_types(self):
        """Получение всех типов задач"""
        sql = "SELECT idtypetask, name FROM typetask ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_roles(self):
        """Получение всех ролей"""
        sql = "SELECT idrole, name FROM role ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_user_info(self, user_id, field, value):
        """Обновление информации о пользователе"""
        sql = f"UPDATE userr SET {field} = %s WHERE iduser = %s"
        self.cursor.execute(sql, (value, user_id))
        self.connector.commit()
        return self.cursor.rowcount > 0

    def add_entity(self, entity_type, name):
        """Добавление новой сущности (должность, тип задачи и т.д.)"""
        tables = {
            'post': ('post', 'name'),
            'typetask': ('typetask', 'name'),
            'statusdeal': ('statusdeal', 'name'),
            'typedeal': ('typedeal', 'name'),
            'role': ('role', 'name')
        }

        if entity_type not in tables:
            return False

        table, column = tables[entity_type]
        sql = f"INSERT INTO {table} ({column}) VALUES (%s)"
        self.cursor.execute(sql, (name,))
        self.connector.commit()
        return self.cursor.rowcount > 0

    def delete_entity(self, entity_type, entity_id):
        """Удаление сущности (должности, типа задачи и т.д.)"""
        tables = {
            'post': ('post', 'idpost'),
            'typetask': ('typetask', 'idtypetask'),
            'statusdeal': ('statusdeal', 'idstatusdeal'),
            'typedeal': ('typedeal', 'idtypedeal'),
            'role': ('role', 'idrole')
        }

        if entity_type not in tables:
            return False

        table, id_column = tables[entity_type]
        sql = f"DELETE FROM {table} WHERE {id_column} = %s"
        self.cursor.execute(sql, (entity_id,))
        self.connector.commit()
        return self.cursor.rowcount > 0

    """Методы для работы с организациями (клиентами)"""

    def get_all_organizations(self):
        """Получение списка всех организаций"""
        sql = "SELECT idorganization, name, inn, kpp FROM organization"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def create_organization(self, name, inn, kpp):
        """Создание новой организации"""
        sql = "INSERT INTO organization (name, inn, kpp) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (name, inn, kpp))
        self.connector.commit()
        return self.cursor.rowcount > 0

    """Методы для работы с задачами"""

    def get_user_tasks(self, user_id):
        """Получение всех задач пользователя"""
        sql = """SELECT t.idtask, tt.name as type, t.description, 
                        CONCAT(u.firstname, ' ', u.name) as sender,
                        t.date1 as created, t.date2 as deadline, t.completed
                 FROM task t
                 JOIN typetask tt ON t.idtt = tt.idtypetask
                 JOIN userr u ON t.sender = u.iduser
                 WHERE t.recipient = %s
                 ORDER BY t.completed, t.date2"""
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_overdue_tasks(self, user_id):
        """Получение просроченных задач"""
        sql = """SELECT t.idtask, tt.name, t.description, 
                        CONCAT(u.firstname, ' ', u.name), t.date2
                 FROM task t
                 JOIN typetask tt ON t.idtt = tt.idtypetask
                 JOIN userr u ON t.sender = u.iduser
                 WHERE t.recipient = %s AND t.date2 < CURDATE() 
                 AND t.completed = FALSE
                 ORDER BY t.date2"""
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_today_tasks(self, user_id):
        """Получение задач на сегодня"""
        sql = """SELECT t.idtask, tt.name, t.description, 
                        CONCAT(u.firstname, ' ', u.name), t.date2
                 FROM task t
                 JOIN typetask tt ON t.idtt = tt.idtypetask
                 JOIN userr u ON t.sender = u.iduser
                 WHERE t.recipient = %s AND DATE(t.date2) = CURDATE()
                 AND t.completed = FALSE
                 ORDER BY t.date2"""
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_future_tasks(self, user_id):
        """Получение будущих задач"""
        sql = """SELECT t.idtask, tt.name, t.description, 
                        CONCAT(u.firstname, ' ', u.name), t.date2
                 FROM task t
                 JOIN typetask tt ON t.idtt = tt.idtypetask
                 JOIN userr u ON t.sender = u.iduser
                 WHERE t.recipient = %s AND t.date2 > CURDATE()
                 AND t.completed = FALSE
                 ORDER BY t.date2"""
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def complete_task(self, task_id):
        """Отметка задачи как выполненной"""
        sql = "UPDATE task SET completed = TRUE, date2 = NOW() WHERE idtask = %s"
        self.cursor.execute(sql, (task_id,))
        self.connector.commit()
        return self.cursor.rowcount > 0

    def get_task_types(self):
        """Получение типов задач"""
        sql = "SELECT idtypetask, name FROM typetask ORDER BY name"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_other_users(self, current_user_email):
        """Получение списка других пользователей"""
        sql = """SELECT iduser, CONCAT(firstname, ' ', name) as fullname 
                 FROM userr 
                 WHERE iduser != (SELECT iduser FROM userr WHERE email = %s)
                 ORDER BY firstname, name"""
        self.cursor.execute(sql, (current_user_email,))
        return self.cursor.fetchall()

    def create_task(self, task_type_id, description, sender_id, recipient_id, deadline):
        """Создание новой задачи"""
        sql = """INSERT INTO task (idtt, description, sender, recipient, date1, date2, completed)
                 VALUES (%s, %s, %s, %s, NOW(), %s, FALSE)"""
        self.cursor.execute(sql, (task_type_id, description, sender_id, recipient_id, deadline))
        self.connector.commit()
        return self.cursor.rowcount > 0

    """Методы для работы с сотрудниками"""

    def get_all_employees(self):
        """Получение списка всех сотрудников"""
        sql = """SELECT u.firstname, u.name, u.lastname, u.email, 
                         r.name as role, p.name as post
                  FROM userr u
                  JOIN role r ON u.idr = r.idrole
                  JOIN post p ON u.idp = p.idpost"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_role_id_by_name(self, role_name):
        """Получение ID роли по названию"""
        sql = "SELECT idrole FROM role WHERE name = %s"
        self.cursor.execute(sql, (role_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_post_id_by_name(self, post_name):
        """Получение ID должности по названию"""
        sql = "SELECT idpost FROM post WHERE name = %s"
        self.cursor.execute(sql, (post_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def create_employee(self, firstname, name, lastname, email, password, role_id, post_id):
        """Создание нового сотрудника"""
        sql = """INSERT INTO userr (firstname, name, lastname, email, password, idr, idp) 
                 VALUES (%s, %s, %s, %s, SHA2(%s, 256), %s, %s)"""
        self.cursor.execute(sql, (firstname, name, lastname, email, password, role_id, post_id))
        self.connector.commit()
        return self.cursor.rowcount > 0

    """Методы для работы с календарем"""

    def get_user_task_dates(self, user_id):
        """Получение дат задач пользователя"""
        sql = """SELECT date2 FROM task 
                   WHERE recipient = %s AND date2 IS NOT NULL"""
        self.cursor.execute(sql, (user_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_user_deal_dates(self, user_id):
        """Получение дат сделок пользователя"""
        sql = """SELECT date2 FROM deal 
                   WHERE executor = %s AND date2 IS NOT NULL"""
        self.cursor.execute(sql, (user_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_tasks_for_date(self, user_id, date_str):
        """Получение задач на определенную дату"""
        sql = """SELECT t.description, tt.name, 
                   CONCAT(u.firstname, ' ', u.name) as sender
                   FROM task t
                   JOIN typetask tt ON t.idtt = tt.idtypetask
                   JOIN userr u ON t.sender = u.iduser
                   WHERE t.recipient = %s 
                   AND DATE(t.date2) = %s"""
        self.cursor.execute(sql, (user_id, date_str))
        return self.cursor.fetchall()

    def get_deals_for_date(self, user_id, date_str):
        """Получение сделок на определенную дату"""
        sql = """SELECT d.name, td.name as type, sd.name as status
                   FROM deal d
                   JOIN typedeal td ON d.idtd = td.idtypedeal
                   JOIN statusdeal sd ON d.idsd = sd.idstatusdeal
                   WHERE d.executor = %s 
                   AND DATE(d.date2) = %s"""
        self.cursor.execute(sql, (user_id, date_str))
        return self.cursor.fetchall()

    """Методы для работы с чатом"""

    def get_chat_users(self, current_user_id):
        """Получение списка пользователей для чата"""
        sql = """SELECT userr.iduser, userr.firstname, userr.name, userr.lastname, post.name 
                     FROM userr 
                     JOIN post ON userr.idp = post.idpost
                     WHERE userr.iduser != %s"""
        self.cursor.execute(sql, (current_user_id,))
        return self.cursor.fetchall()

    def get_chat_messages(self, sender_id, recipient_id):
        """Получение сообщений между двумя пользователями"""
        sql = """SELECT sender, recipient, message_text, sent_at 
                     FROM messages 
                     WHERE (sender = %s AND recipient = %s) OR 
                           (sender = %s AND recipient = %s)
                     ORDER BY sent_at"""
        self.cursor.execute(sql, (sender_id, recipient_id, recipient_id, sender_id))
        return self.cursor.fetchall()

    def send_message(self, sender_id, recipient_id, message_text):
        """Отправка сообщения"""
        sql = "INSERT INTO messages (sender, recipient, message_text, sent_at) VALUES (%s, %s, %s, NOW())"
        self.cursor.execute(sql, (sender_id, recipient_id, message_text))
        self.connector.commit()
        return self.cursor.rowcount > 0

    """Методы для аналитики"""

    def get_deals_distribution(self):
        """Получение распределения сделок по статусам"""
        sql = """SELECT sd.name, COUNT(d.iddeal)
                 FROM deal d
                 JOIN statusdeal sd ON d.idsd = sd.idstatusdeal
                 GROUP BY sd.name"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_tasks_distribution(self, user_id):
        """Получение распределения задач по типам для пользователя"""
        sql = """SELECT tt.name, COUNT(t.idtask)
                 FROM task t
                 JOIN typetask tt ON t.idtt = tt.idtypetask
                 WHERE t.recipient = %s
                 GROUP BY tt.name"""
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_deals_by_status(self, status_id):
        """Получение сделок по статусу"""
        sql = """SELECT d.name, td.name as type, o.name as organization,
                        CONCAT(u.firstname, ' ', u.name) as executor, d.date2
                 FROM deal d
                 JOIN typedeal td ON d.idtd = td.idtypedeal
                 JOIN organization o ON d.ido = o.idorganization
                 JOIN userr u ON d.executor = u.iduser
                 WHERE d.idsd = %s"""
        self.cursor.execute(sql, (status_id,))
        return self.cursor.fetchall()

    def get_tasks_by_type(self, type_id, user_id=None):
        """Получение задач по типу (опционально для конкретного пользователя)"""
        sql = """SELECT t.description, CONCAT(u.firstname, ' ', u.name) as sender, t.date2
                 FROM task t
                 JOIN userr u ON t.sender = u.iduser
                 WHERE t.idtt = %s"""
        params = [type_id]

        if user_id:
            sql += " AND t.recipient = %s"
            params.append(user_id)

        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def get_deals_summary(self):
        """Получение сводной информации по сделкам"""
        sql = """SELECT 
                    COUNT(iddeal) as total_deals,
                    SUM(CASE WHEN idsd = 1 THEN 1 ELSE 0 END) as new_deals,
                    SUM(CASE WHEN idsd = 2 THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN idsd = 3 THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN idsd = 4 THEN 1 ELSE 0 END) as cancelled,
                    COALESCE(SUM(total_price), 0) as total_amount
                 FROM deal"""
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_tasks_summary(self, user_id=None):
        """Получение сводной информации по задачам"""
        sql = """SELECT 
                    COUNT(idtask) as total_tasks,
                    SUM(CASE WHEN completed = TRUE THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN completed = FALSE AND date2 < CURDATE() THEN 1 ELSE 0 END) as overdue,
                    SUM(CASE WHEN completed = FALSE AND date2 >= CURDATE() THEN 1 ELSE 0 END) as active
                 FROM task"""

        params = []
        if user_id:
            sql += " WHERE recipient = %s"
            params.append(user_id)

        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def close(self):
        """Закрыть соединение с БД"""
        self.connector.close()