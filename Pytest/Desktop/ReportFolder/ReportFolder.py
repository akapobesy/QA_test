import os
import logging
from datetime import datetime


class ReportFolder:
    def __init__(self, base_path="C:/Reports"):
        self.base_path = base_path

    def _setup_logging(self, log_path):
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def create_folder(self, final_folder=None):
        time_now = datetime.now()
        time_day_now = time_now.strftime("%Y.%m.%d")

        dir_path = os.path.join(self.base_path, time_day_now)

        if final_folder:
            dir_path = os.path.join(dir_path, final_folder)

        try:
            os.makedirs(dir_path, exist_ok=True)

            log_path = os.path.join(dir_path, "Report.log")

            # Настройка логирования
            self._setup_logging(log_path)

            logging.info(f"Папка создана: {dir_path}")

            return dir_path

        except Exception as e:
            logging.error(f"Ошибка при создании папки: {e}")
            return None
