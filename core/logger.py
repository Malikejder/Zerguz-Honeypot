# core/logger.py

import logging
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


class ZerguzLogger:
    """
    Centralized logging component for Zerguz.
    Handles console and file logging.
    """

    LOG_FILE = "zerguz_alerts.log"

    def __init__(self) -> None:

        Path(self.LOG_FILE).touch(exist_ok=True)

        self.logger = logging.getLogger("Zerguz")

        if self.logger.handlers:
            return

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(
            self.LOG_FILE,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    # --------------------------------------------------
    # Console Methods
    # --------------------------------------------------

    @staticmethod
    def info(message: str) -> None:
        print(Fore.CYAN + "[*] " + message)

    @staticmethod
    def success(message: str) -> None:
        print(Fore.GREEN + "[+] " + message)

    @staticmethod
    def warning(message: str) -> None:
        print(Fore.YELLOW + "[!] " + message)

    @staticmethod
    def error(message: str) -> None:
        print(Fore.RED + "[-] " + message)

    # --------------------------------------------------
    # File Logging Methods
    # --------------------------------------------------

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    # --------------------------------------------------
    # Security Events
    # --------------------------------------------------

    def log_attack(self, ip: str, port: int) -> None:

        message = (
            f"[ZERGUZ DETECT] "
            f"Attack detected | "
            f"Source IP={ip} | "
            f"Destination Port={port}"
        )

        self.warning(
            f"Attack detected -> {ip}:{port}"
        )

        self.log_warning(message)

    def log_block(self, ip: str) -> None:

        message = (
            f"[ZERGUZ DEFENSE] "
            f"Firewall blocked IP={ip}"
        )

        self.success(
            f"IP blocked -> {ip}"
        )

        self.log_info(message)
