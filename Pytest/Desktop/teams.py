import logging
import os
import time
import sys
import pyautogui
import glob
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

url = 'https://statics.teams.cdn.office.net/production-windows-x86/lkg/MSTeamsSetup.exe'
TEAMS_INSTALLER_PATH = r"C:\Teams.exe"
#TEAMS_EXE_PATH = find_teams_exe_windowsapps()
TEAMS_VERSION_FILE = r'C:\teams_version.txt'
FILE_TO_SEND1 = r"C:\files\Teams.pdf"
#FILE_TO_SEND2 = r"C:\files\file2.pdf"
#FILE_TO_SEND3 = r"C:\files\file3.pdf"
name_mess = 'Teams'
install_args = ["/-s"]

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def check_installer_exists(installer_path):
    if not os.path.exists(installer_path):
        logging.error(f"Файл установщика не найден: {installer_path}")
        return False
    return True  
 
def messeges_teams():
    logging.info(f"Начало отправки сообщения {name_mess}")

    time.sleep(2)

    message_field = pyautogui.locateCenterOnScreen('screens/teams_field.png', confidence=0.8)
    if message_field:
        pyautogui.click(message_field)
        time.sleep(1)
        message_sender = Messages("This is test messages_teams")
        message_sender.run(5)
        logging.info("Сообщения отправлены")
    else:
        logging.error("Поле ввода сообщения не найдено")
        return 

def wait_and_click(image_path, timeout=15, confidence=0.8):
    start_time = time.time()

    while time.time() - start_time < timeout:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            logging.info(f"Элемент найден и нажат: {image_path}")
            return True

        time.sleep(0.5)

    logging.error(f"Элемент не найден за {timeout} секунд: {image_path}")
    return False 
        
def check_database():
    try:
        db = DatabaseReporter(DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME)
        db.connect()

        # Проверка сообщений
        messages = db.fetch_messages(
            'SELECT conv_message_body FROM conv_messages LIMIT 500;'
        )

        if db.message_exists(messages, 'This is test messages_teams'):
            logging.info('Сообщение найдено в БД')
        else:
            logging.warning('Сообщение не найдено в БД')

        # Проверка файлов
        files = db.fetch_messages(
            "SELECT conv_file_fname FROM conv_files LIMIT 100;"
        )

        if db.message_exists(files, 'Teams.pdf'):
            logging.info('Файл найден в БД')
        else:
            logging.warning('Файл не найден в БД')

        db.close()

    except Exception:
        logging.exception("Ошибка при работе с БД")
        
def find_teams_exe_windowsapps():
    base_path = r"C:\Program Files\WindowsApps"
    pattern = os.path.join(base_path, "MSTeams_*", "ms-teams.exe")
    matches = glob.glob(pattern)
    if matches:
        exe_path = matches[0]
        logging.info(f"Teams.exe найден: {exe_path}")
        return exe_path
    else:
        logging.error(f"{name_mess}.exe в WindowsApps не найден!")
        return None

TEAMS_EXE_PATH = find_teams_exe_windowsapps()

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
         #0. Логирование
        report = ReportFolder("C:/Reports/Rocketchat")
        folder_path = report.create_folder()

        # 1. Скачивание
        downloader = DownloaderInstl(url, TEAMS_INSTALLER_PATH)

        if not downloader.attempt_download():
            logging.critical("Загрузка не удалась. Остановка процесса.")
            return

        time.sleep(5)
    
        # 2. Установка
        if check_installer_exists(TEAMS_INSTALLER_PATH):

            installer = AppInstaller(
                installer_path=TEAMS_INSTALLER_PATH,
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

            while not os.path.exists(TEAMS_EXE_PATH):
                elapsed = time.time() - start_time

                if elapsed >= timeout:
                    break

                time.sleep(interval)

            if os.path.exists(TEAMS_EXE_PATH):
                logging.info(f"{name_mess} успешно установлен: {TEAMS_EXE_PATH}")
            else:
                logging.error(f"После установки {name_mess}.exe не найден! Проверьте установщик или права доступа.")
                
                return
        
        # 3. Версия 
        if os.path.exists(TEAMS_EXE_PATH):
            version_manager = FileVersionManager(
                TEAMS_EXE_PATH,
                TEAMS_VERSION_FILE
            )
            version_manager.process_version()
        else:
            logging.error(f"{name_mess}.exe не найден после установки")
            return  

        time.sleep(5)      

        # 4. Запуск Teams
        #teams = StartApp(TEAMS_EXE_PATH)
        #teams.run()
        #time.sleep(3)

        # 5. Автоматизация
        messeges_teams()

        # 6. Отправка файла
        if not wait_and_click('screens/teams2.png', timeout=15):
            return
        time.sleep(1)
        if not wait_and_click('screens/teams3.png', timeout=15):
            return
        time.sleep(1)
        if not wait_and_click('screens/teams4.png', timeout=15):
            return
        time.sleep(1)
        if not wait_and_click('screens/teams5.png', timeout=15):
            return
        time.sleep(2)
        pyautogui.typewrite(r'C:\files\Teams.pdf')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3)
        pyautogui.press('enter')
        time.sleep(3)

        # 7. Проверка БД
        check_database()

        #8. Закрытие приложения
        close_app_by_name("ms-teams.exe")

        logging.info("=== Автоматизация завершена успешно ===")

    except Exception:
        logging.exception("Критическая ошибка в процессе выполнения")


if __name__ == "__main__":
    main()
