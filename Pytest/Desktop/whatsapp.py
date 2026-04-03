import logging
import os
import time
import sys
import pyautogui
import glob
import subprocess
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

# Переменные БД (через ENV безопаснее)
DB_HOST = os.getenv("DB_HOST", "10.10.11.111")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "1234")
DB_NAME = os.getenv("DB_NAME", "test0502")

#url = ''
#WHATSAPP_INSTALLER_PATH = ''
WHATSAPP_VERSION_FILE = r'C:\whatsapp_version.txt'
FILE_TO_SEND1 = r"C:\files\Whatsapp.pdf"
#FILE_TO_SEND2 = r"C:\files\file2.pdf"
#FILE_TO_SEND3 = r"C:\files\file3.pdf"
name_mess = 'Whatsapp'

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================


def install_whatsapp_with_winget():   
    command = [
        "powershell",
        "-Command",
        "winget install --id 9NKSQGP7F2NH --source msstore --accept-package-agreements"
    ]
    
    try:
        logging.info(f"Запуск установки {name_mess} через winget...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info(f"Установка {name_mess} через winget завершена успешно.")
            logging.info(result.stdout)
            return True
        else:
            logging.error(f"Ошибка при установке через winget. Код выхода: {result.returncode}")
            logging.error(result.stdout)
            logging.error(result.stderr)
            return False

    except Exception as e:
        logging.exception(f"Исключение при запуске winget: {e}")
        return False

def start_whatsapp():
    logging.info(f"Старт {name_mess}")
    time.sleep(2)

    message_field = pyautogui.locateCenterOnScreen('screens/whatsapp.png', confidence=0.8)
    if message_field:
        pyautogui.click(message_field)
        time.sleep(1)       
    else:
        logging.error("Ошибка запуска прилоежния")
        return

def messeges_whatsapp():
    logging.info(f"Начало автоматизации {name_mess}")

    time.sleep(2)

    search_field = pyautogui.locateCenterOnScreen('screens/whatsapp_icon.png', confidence=0.8)
    if search_field:
        pyautogui.click(search_field)
        time.sleep(1)        
        logging.info("Пользователь выбран")
    else:
        logging.error("Поле поиска не найдено на экране")
        return

    time.sleep(1)

    message_field = pyautogui.locateCenterOnScreen('screens/whatsapp_field.png', confidence=0.8)
    if message_field:
        pyautogui.click(message_field)
        time.sleep(1)
        message_sender = Messages("This is test messages_whatsapp")
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

        if db.message_exists(messages, 'This is test messages_whatsapp'):
            logging.info('Сообщение найдено в БД')
        else:
            logging.warning('Сообщение не найдено в БД')

        # Проверка файлов
        files = db.fetch_messages(
            "SELECT conv_file_fname FROM conv_files LIMIT 100;"
        )

        if db.message_exists(files, 'Whatsapp.pdf'):
            logging.info('Файл найден в БД')
        else:
            logging.warning('Файл не найден в БД')

        db.close()

    except Exception:
        logging.exception("Ошибка при работе с БД")
        
def find_whatsapp_exe_windowsapps():
    base_path = r"C:\Program Files\WindowsApps"
    pattern = os.path.join(base_path, "*WhatsAppDesktop_*", "WhatsApp.Root.exe")
    matches = glob.glob(pattern)
    if matches:
        exe_path = matches[0]
        logging.info(f"WhatsApp.Root.exe найден: {exe_path}")
        return exe_path
    else:
        logging.error("WhatsApp.Root.exe в WindowsApps не найден!")
        return None

WHATSAPP_EXE_PATH = find_whatsapp_exe_windowsapps()

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



# ===================== ОСНОВНОЙ ПРОЦЕСС =====================

def main():
    logging.info("=== Запуск автоматизации ===")

    try: 
        # 0. настройка логирования
        report = ReportFolder("C:/Reports/WhatsApp")
        folder_path = report.create_folder()
      
        # 1. Установка
        logging.info(f"=== Запуск установки {name_mess} через Winget ===")
    
        if install_whatsapp_with_winget():
            logging.info(f"{name_mess} установлен успешно.")
        else:
            logging.error(f"Не удалось установить {name_mess} через Winget.")
        
        time.sleep(5)
        
        # 2. Версия
        if os.path.exists(WHATSAPP_EXE_PATH):
            version_manager = FileVersionManager(
                WHATSAPP_EXE_PATH,
                WHATSAPP_VERSION_FILE
            )
            version_manager.process_version()
        else:
            logging.error(f"{name_mess}.exe не найден после установки")
            return
        
        # 3. Старт
        start_whatsapp()
        time.sleep(7)
        
        # 4. Сообщения
        messeges_whatsapp()

        # 6. Отправка файла
        for file in [FILE_TO_SEND1]:
            send_file(file)
        time.sleep(3)

        # 7. Проверка БД
        check_database()

        #8. Закрытие приложения
        close_app_by_name("WhatsApp.Root.exe")

        logging.info("=== Автоматизация завершена успешно ===")

    except Exception:
        logging.exception("Критическая ошибка в процессе выполнения")


if __name__ == "__main__":
    main()
