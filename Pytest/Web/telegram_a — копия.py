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
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

file = "C:\files\Telegramweba.pdf"
#FILE_TO_SEND2 = r"C:\files\file2.pdf"
#FILE_TO_SEND3 = r"C:\files\file3.pdf"
name_mess = 'Telegram'


# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def open_telegram(profile_path: str, profile_name: str = "Default", url: str = "https://web.telegram.org/a/", timeout: int = 15):
    
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


        chat = driver.find_element(By.CSS_SELECTOR, '[alt="Олег"]')
        chat.click()
        place = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.ID, 'editable-message-text'))
        )            
        place.click()
        place.send_keys("Test message")
        place.send_keys(Keys.ENTER)

        files1 = driver.find_element(By.CSS_SELECTOR, ".icon.icon-attach")
        files1.click()
        files2 = driver.find_element(By.CSS_SELECTOR, "#attach-menu-controls > div > div:nth-child(2)")
        files2.click()
        time.sleep(1)
        pyautogui.write('C:\\files\Telegramweba.pdf')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)        
        logging.info("Файл загружен")             
        press_file = driver.find_element(By.CSS_SELECTOR, '[class="Button kNlWmBJI smaller primary inline"]')
        press_file.click()
        time.sleep(2)
       

        




        return driver, wait

    except Exception as e:
        logging.error(f"Ошибка при запуске {name_mess}")
        logging.error(traceback.format_exc())
        raise

def main():
    logging.info("=== Запуск автоматизации ===")

    try:
         #0. Логирование
        report = ReportFolder("C:/Reports/Web/Telegram_k")
        folder_path = report.create_folder()

        driver, wait = open_telegram(profile_path)

        time.sleep(3)        

    except Exception:
        logging.exception("Критическая ошибка в процессе выполнения")


if __name__ == "__main__":
    main()
