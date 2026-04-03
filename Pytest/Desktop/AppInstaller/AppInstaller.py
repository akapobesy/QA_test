import subprocess
import logging
import os

class AppInstaller:
    def __init__(self, installer_path, install_args=None):
        self.installer_path = installer_path
        self.install_args = install_args or []

    def get_install_command(self):
        ext = os.path.splitext(self.installer_path)[1].lower()

        # Если MSI — запускаем через msiexec
        if ext == ".msi":
            return [
                "msiexec",
                "/i",
                self.installer_path,
                "/qn",
                "/norestart",
            ] + self.install_args

        # Если EXE — запускаем напрямую
        return [self.installer_path] + self.install_args

    def install(self, timeout=None):
        if not os.path.exists(self.installer_path):
            logging.error("Файл инсталлятора не найден.")
            return False

        command = self.get_install_command()
        logging.info(f"Запуск установки: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                check=False
            )

            if result.returncode != 0:
                logging.error(f"Установщик завершился с кодом: {result.returncode}")
                return False

            logging.info("Установка завершена успешно.")
            return True

        except subprocess.TimeoutExpired:
            logging.error("Превышено время ожидания установки.")
            return False

        except OSError as e:
            logging.exception(f"Ошибка запуска процесса: {e}")
            return False

        except Exception as e:
            logging.exception(f"Неожиданная ошибка: {e}")
            return False
