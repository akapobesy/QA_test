import os
import time
import logging


class StartApp:
    def __init__(self, app_path):      
        self.app_path = app_path        

    def start_chat(self):
        if os.path.isfile(self.app_path):
            try:
                logging.info(f"Запуск приложения: {self.app_path}")
                os.startfile(self.app_path)
                time.sleep(2)
                logging.info("Приложение успешно запущено.")
            except Exception as e:
                logging.error(f"Произошла ошибка при запуске приложения: {e}")
        else:
            logging.warning("Указанный путь к приложению не существует.")

    def run(self):
        self.start_chat()

