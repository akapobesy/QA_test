import logging
import os
import time
import sys
import pyautogui
import requests
import urllib.request
import yaml
import ssl
import threading
import psutil

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl

from DownloaderInstl import DownloaderInstl
from AppInstaller import AppInstaller
from FileVersionManager import FileVersionManager
from StartApp import StartApp
from Messages import Messages
from DatabaseReporter import DatabaseReporter
from ReportFolder import ReportFolder


# ===================== НАСТРОЙКИ =====================

ssl._create_default_https_context = ssl._create_unverified_context

# Переменные БД (через ENV безопаснее)
DB_HOST = os.getenv("DB_HOST", "10.10.11.111")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "test0502")

SIGNAL_YAML_URL = "https://updates.signal.org/desktop/latest.yml"

def get_signal_download_url(arch="x64"):
    try:
        logging.info(f"Скачиваем latest.yml с {SIGNAL_YAML_URL}")
        with urllib.request.urlopen(SIGNAL_YAML_URL) as response:
            yaml_content = response.read().decode("utf-8")

        data = yaml.safe_load(yaml_content)

        # Ищем нужный файл по архитектуре
        for f in data.get("files", []):
            url = f.get("url")
            if arch in url:
                full_url = f"https://updates.signal.org/desktop/{url}"
                logging.info(f"Найден файл для {arch}: {full_url}")
                return full_url

        logging.error(f"Файл для архитектуры {arch} не найден")
        return None

    except Exception as e:
        logging.error(f"Ошибка при получении ссылки на Signal: {e}")
        return None

SIGNAL_YAML_URL = "https://updates.signal.org/desktop/latest.yml"
SIGNAL_INSTALLER_PATH = r"C:\Signal.exe"
SIGNAL_EXE_PATH = r'C:\Users\user02\AppData\Local\Programs\signal-desktop\Signal.exe'
SIGNAL_VERSION_FILE = r'C:\signal_version.txt'
FILE_TO_SEND1 = r"C:\files\Signal.pdf"
#FILE_TO_SEND2 = r"C:\files\file2.pdf"
#FILE_TO_SEND3 = r"C:\files\file3.pdf"
destination = SIGNAL_INSTALLER_PATH
name_mess = 'Signal'
install_args = ["/S"]

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def download_signal_from_yaml(yaml_url: str, path: str, arch: str = "x64", max_attempts: int = 5, initial_timeout: int = 30) -> bool:
    
    try:
        logging.info(f"Получаем YAML с {yaml_url}")
        yaml_text = requests.get(yaml_url).text
        doc = yaml.safe_load(yaml_text)

        # ищем файл под нужную архитектуру
        signal_url = None
        for f in doc.get("files", []):
            url_file = f.get("url")
            if arch in url_file:
                signal_url = f"https://updates.signal.org/desktop/{url_file}"
                sha512 = f.get("sha512", "")
                logging.info(f"Найден файл для {arch}: {signal_url}")
                logging.info(f"SHA512: {sha512}")
                break

        if not signal_url:
            logging.error(f"Файл для архитектуры {arch} не найден в YAML")
            return False

    except Exception as e:
        logging.critical(f"Не удалось получить ссылку на Signal: {e}")
        return False

    waiting_time = initial_timeout

    # функция скачивания с user-agent
    def download_file():
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(signal_url, path)

    for attempt in range(1, max_attempts + 1):
        # удаляем старый файл
        if os.path.exists(path):
            try:
                os.remove(path)
                logging.info(f"Удалён предыдущий файл {path}")
            except Exception as e:
                logging.warning(f"Не удалось удалить старый файл: {e}")

        t = threading.Thread(target=download_file)
        t.start()
        t.join(waiting_time)

        if t.is_alive():
            logging.warning(f"Попытка {attempt}: не удалось скачать за {waiting_time} секунд")
            waiting_time += 10
        elif os.path.exists(path) and os.path.getsize(path) > 0:
            logging.info(f"Попытка {attempt}: файл успешно скачан в {path}")
            return True
        else:
            logging.warning(f"Попытка {attempt}: файл скачан, но он пустой")
            time.sleep(2)

    logging.critical(f"Не удалось скачать {name_mess} после нескольких попыток")
    return False

def check_installer_exists(installer_path):
    if not os.path.exists(installer_path):
        logging.error(f"Файл установщика не найден: {installer_path}")
        return False
    return True

def messeges_signal():
    logging.info(f"Начало автоматизации {name_mess}")

    time.sleep(2)

    search_field = pyautogui.locateCenterOnScreen('screens/signal_icon.png', confidence=0.8)
    if search_field:
        pyautogui.click(search_field)
        time.sleep(1)        
        logging.info("Пользователь выбран")
    else:
        logging.error("Поле поиска не найдено на экране")
        return

    time.sleep(1)

    message_field = pyautogui.locateCenterOnScreen('screens/signal_field.png', confidence=0.8)
    if message_field:
        pyautogui.click(message_field)
        time.sleep(1)
        message_sender = Messages("This is test messages_signal")
        message_sender.run(5)
        logging.info("Сообщения отправлены")
    else:
        logging.error("Поле ввода сообщения не найдено")
        return
    
def copy_file_to_clipboard(file_path):
    if not os.path.isfile(file_path):
        raise ValueError(f"Файл не найден: {file_path}")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    mime_data = QMimeData()
    file_url = QUrl.fromLocalFile(file_path)
    mime_data.setUrls([file_url])

    clipboard = app.clipboard()
    clipboard.setMimeData(mime_data)

    logging.info(f"Файл '{file_path}' скопирован в буфер обмена.")

def send_file(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Файл для отправки не найден: {file_path}")
        return
    try:
        copy_file_to_clipboard(file_path)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        logging.info(f"Файл '{file_path}' отправлен")
    except Exception:
        logging.exception(f"Ошибка при отправке файла '{file_path}'")


def check_database():
    try:
        db = DatabaseReporter(DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME)
        db.connect()

        # Проверка сообщений
        messages = db.fetch_messages(
            'SELECT conv_message_body FROM conv_messages LIMIT 500;'
        )

        if db.message_exists(messages, 'This is test messages_signal'):
            logging.info('Сообщение найдено в БД')
        else:
            logging.warning('Сообщение не найдено в БД')

        # Проверка файлов
        files = db.fetch_messages(
            "SELECT conv_file_fname FROM conv_files LIMIT 100;"
        )

        if db.message_exists(files, 'Signal.pdf'):
            logging.info('Файл найден в БД')
        else:
            logging.warning('Файл не найден в БД')

        db.close()

    except Exception:
        logging.exception("Ошибка при работе с БД")

def close_app_by_name(process_name):
   
    found = False

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                logging.info(f"Завершаем процесс {process_name} (PID {proc.pid})")
                proc.terminate()
                proc.wait(timeout=10)
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found:
        logging.info(f"Процесс {process_name} не найден.")


def main():
    logging.info("=== Запуск автоматизации ===")

    try:
         #0. Логирование
        report = ReportFolder("C:/Reports/Signal")
        folder_path = report.create_folder()
        
        # 1. Скачивание
        if download_signal_from_yaml(SIGNAL_YAML_URL, SIGNAL_INSTALLER_PATH):
            logging.info(f"{name_mess} готов к установке")
        else:
            logging.error(f"Не удалось скачать {name_mess}, остановка процесса")
            
        # 2. Установка
        if check_installer_exists(SIGNAL_INSTALLER_PATH):

            installer = AppInstaller(
                installer_path=SIGNAL_INSTALLER_PATH,
                install_args=install_args
            )

            success = installer.install(timeout=300)

            if not success:
                logging.critical(f"Установка {name_mess} завершилась с ошибкой. Остановка процесса.")
                return

            # -------- Проверка появления exe --------
            timeout = 60
            interval = 5
            elapsed = 0

            logging.info(f"Ожидание появления {name_mess}.exe после установки...")

            start_time = time.time()

            while not os.path.exists(SIGNAL_EXE_PATH):
                elapsed = time.time() - start_time

                if elapsed >= timeout:
                    break

                time.sleep(interval)

            if os.path.exists(SIGNAL_EXE_PATH):
                logging.info(f"{name_mess} успешно установлен: {SIGNAL_EXE_PATH}")
            else:
                logging.error(f"После установки {name_mess}.exe не найден! Проверьте установщик или права доступа.")
                
                return

        else:
            logging.error(f"Установочный файл не найден: {SIGNAL_INSTALLER_PATH}")
            return

        time.sleep(3)

        # 3. Версия
        if os.path.exists(SIGNAL_EXE_PATH):
            version_manager = FileVersionManager(
                SIGNAL_EXE_PATH,
                SIGNAL_VERSION_FILE
            )
            version_manager.process_version()
        else:
            logging.error(f"{name_mess}.exe не найден после установки")
            return

        # 4. Запуск
        signal = StartApp(SIGNAL_EXE_PATH)
        signal.run()

        time.sleep(5)

        # 5. Отправка сообщений
        messeges_signal()

        # 6. Отправка файла
        for file in [FILE_TO_SEND1]:
            send_file(file)
            
        time.sleep(3)

        # 7. Проверка БД
        check_database()

        #8. Закрытие приложения
        close_app_by_name("Signal.exe")

        logging.info("=== Автоматизация завершена успешно ===")

    except Exception:
        logging.exception("Критическая ошибка в процессе выполнения")


if __name__ == "__main__":
    main()
