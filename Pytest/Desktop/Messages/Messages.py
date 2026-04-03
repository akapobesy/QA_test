import pyautogui
import string
import random
import logging
import time

class Messages:
    def __init__(self, initial_message):
        self.initial_message = initial_message        

    def send_test_messages(self):        
        pyautogui.typewrite(self.initial_message) 
        pyautogui.press('enter')  
        logging.info("Начальное тестовое сообщение отправлено")
        time.sleep(1)

    def send_random_messages(self, count):
        for i in range(count):
            word = self.generate_random_word(10)            
            pyautogui.typewrite(word)
            pyautogui.press('enter')
            logging.info("Случайное сообщение отправлено: '%s'", word)
            time.sleep(1)

    def generate_random_word(self, length):
        letters = string.ascii_lowercase 
        random_word = ''.join(random.choice(letters) for i in range(length))
        return random_word

    def run(self, count):
        logging.info("Запуск отправки сообщений")
        self.send_test_messages()  
        self.send_random_messages(count)
        logging.info("Отправка сообщений завершена")
