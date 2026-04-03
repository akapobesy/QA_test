import logging
import psycopg2
from psycopg2 import OperationalError

class DatabaseReporter:
    def __init__(self, host, port, user, password, dbname):
        self.connection_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'dbname': dbname
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
            logging.info('Подключение успешно!')
        except OperationalError as e:
            logging.error(f'Ошибка подключения: {e}', exc_info=True)

    def fetch_messages(self, query):
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            #logging.info(f'Результаты запроса: {results}')
            return results
        except Exception as e:
            logging.error(f'Ошибка выполнения запроса: {e}', exc_info=True)
            return []

    def message_exists(self, results, message):
        if not results:
            return False
        return any(message in row[0] for row in results)

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logging.info('Соединение закрыто')
        except Exception as e:
            logging.error(f'Ошибка при закрытии соединения: {e}', exc_info=True)
