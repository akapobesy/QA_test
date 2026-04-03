import logging
import os
import time
import sys
import pyautogui
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl

from Messages import Messages
from DatabaseReporter import DatabaseReporter
from ReportFolder import ReportFolder


# ===================== НАСТРОЙКИ =====================

# Переменные БД (через ENV безопаснее)
DB_HOST = os.getenv("DB_HOST", "10.10.11.111")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "test0502")

profile_path = r"C:\ChromeSeleniumProfile"

FILE_TO_SEND1 = r"C:\files\Telegramwebk.pdf"
#FILE_TO_SEND2 = r"C:\files\file2.pdf"
#FILE_TO_SEND3 = r"C:\files\file3.pdf"
name_mess = 'Telegram'


# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def open_telegram(profile_path: str, profile_name: str = "Default", url: str = "https://web.telegram.org/k/", timeout: int = 15):
    
    try:
        logging.info("Запуск браузера")

        options = Options()
        options.add_argument(f"user-data-dir={profile_path}")
        options.add_argument(f"--profile-directory={profile_name}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, timeout)

        logging.info(f"Открываем {name_mess} Web")
        driver.get(url)

        driver.implicitly_wait(5)

        logging.info(f"{name_mess} успешно открыт")

        return driver, wait

    except Exception as e:
        logging.error(f"Ошибка при запуске {name_mess}")
        logging.error(traceback.format_exc())
        raise

def messeges_telegram():
    logging.info(f"Начало автоматизации {name_mess}")
    time.sleep(2)
    
    search_field = pyautogui.locateCenterOnScreen('Screens/telegram_icon.png', confidence=0.8)
    if search_field:
        pyautogui.click(search_field)
        time.sleep(1)        
        logging.info("Пользователь выбран")
    else:
        logging.error("Поле поиска не найдено на экране")
        return

    time.sleep(1)
   
    message_field = pyautogui.locateCenterOnScreen('Screens/telegram_field.png', confidence=0.8)
    if message_field:
        pyautogui.click(message_field)
        time.sleep(1)
        message_sender = Messages("This is test messages_telegram_web_k")
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

        if db.message_exists(messages, 'This is test messages_telegram_web_k'):
            logging.info('Сообщение найдено в БД')
        else:
            logging.warning('Сообщение не найдено в БД')

        # Проверка файлов
        files = db.fetch_messages(
            "SELECT conv_file_fname FROM conv_files LIMIT 100;"
        )

        if db.message_exists(files, 'Telegram_web_k.pdf'):
            logging.info('Файл найден в БД')
        else:
            logging.warning('Файл не найден в БД')

        db.close()

    except Exception:
        logging.exception("Ошибка при работе с БД")

def main():
    logging.info("=== Запуск автоматизации ===")

    try:
         #0. Логирование
        report = ReportFolder("C:/Reports/Web/Telegram_k")
        folder_path = report.create_folder()

        driver, wait = open_telegram(profile_path)

        time.sleep(3)

        # 1. Отправка сообщений
        messeges_telegram()

        # 2. Отправка файла
        for file in [FILE_TO_SEND1]:
            send_file(file)

        time.sleep(3)
        
        # 7. Проверка БД
        check_database()

        logging.info("=== Автоматизация завершена успешно ===")

    except Exception:
        logging.exception("Критическая ошибка в процессе выполнения")


if __name__ == "__main__":
    main()
