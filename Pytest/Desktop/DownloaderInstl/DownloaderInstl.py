import time
import urllib.request
import os
import ssl
import logging

ssl._create_default_https_context = ssl._create_unverified_context


class DownloaderInstl:
    def __init__(self, url, destination):
        self.url = url
        self.destination = destination
        self.max_attempts = 5
        self.timeout = 60  # таймаут запроса в секундах

    def download(self):
        try:
            logging.info(f"Начало загрузки {self.url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            request = urllib.request.Request(self.url, headers=headers)

            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                with open(self.destination, "wb") as out_file:
                    out_file.write(response.read())

            if os.path.exists(self.destination) and os.path.getsize(self.destination) > 0:
                logging.info("Скачивание завершено успешно.")
                return True
            else:
                logging.error("Файл пустой после скачивания.")
                return False

        except Exception as e:
            logging.error(f"Ошибка при скачивании: {e}")
            return False

    def attempt_download(self):
        for attempt in range(1, self.max_attempts + 1):

            self.cleanup_previous_download()

            success = self.download()

            if success:
                logging.info(f"Попытка {attempt}: Файл успешно загружен.")
                return True
            else:
                logging.warning(f"Попытка {attempt}: Загрузка не удалась.")
                time.sleep(3)

        logging.error("Не удалось скачать файл после нескольких попыток.")
        return False

    def cleanup_previous_download(self):
        if os.path.exists(self.destination):
            try:
                os.remove(self.destination)
                logging.info("Удален предыдущий файл для повторного скачивания.")
            except Exception as e:
                logging.warning(f"Ошибка при удалении файла: {e}")
