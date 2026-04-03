import os
from win32api import GetFileVersionInfo, LOWORD, HIWORD
import logging

class FileVersionManager:
    def __init__(self, exe_path, version_file_path):
        """
        Инициализация объекта для работы с версией исполняемого файла.
        :param exe_path: путь к исполняемому файлу
        :param version_file_path: путь для сохранения информации о версии
        """
        self.exe_path = exe_path
        self.version_file_path = version_file_path

    def get_version_number(self):
        # Получает версию исполняемого файла
        try:
            logging.info(f"Получение версии файла: {self.exe_path}")
            info = GetFileVersionInfo(self.exe_path, "\\")  
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{HIWORD(ms)}.{LOWORD(ms)}.{HIWORD(ls)}.{LOWORD(ls)}"
            logging.info(f"Версия файла: {version}")
            return version
        except Exception as e:
            logging.error(f"Ошибка при получении версии: {e}")
            return "Unknown version"

    def remove_old_version_file(self):
        # Удаляет предыдущий файл с версией, если он существует
        if os.path.exists(self.version_file_path):
            try:
                os.remove(self.version_file_path)
                logging.info(f"Удален старый файл: {self.version_file_path}")
            except Exception as e:
                logging.error(f"Ошибка при удалении файла: {e}")

    def save_version_to_file(self, version):
        # Сохраняет версию в файл
        try:
            with open(self.version_file_path, 'w') as f:
                f.write(version)
            logging.info(f"Версия {version} сохранена в {self.version_file_path}")
        except Exception as e:
            logging.error(f"Ошибка при записи в файл: {e}")

    def process_version(self):
        # Основной метод для обработки версии файла
        self.remove_old_version_file()
        version = self.get_version_number()
        self.save_version_to_file(version)
