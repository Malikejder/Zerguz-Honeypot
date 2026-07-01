# core/firewall.py

import os
import platform
import shutil
import subprocess
from typing import Set

from core.logger import ZerguzLogger


class ZerguzFirewallManager:
    """
    Manages firewall operations for Zerguz.

    Supported platforms:
        - Linux (ufw / iptables)
        - Windows (netsh advfirewall)
    """

    def __init__(self, logger: ZerguzLogger) -> None:
        self.logger = logger
        self.blocked_ips: Set[str] = set()
        self.os_type = platform.system()

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def block_ip(self, ip: str) -> bool:
        """
        Blocks an IP address if it is not already blocked.
        """

        if ip in self.blocked_ips:
            self.logger.info(
                f"IP already blocked: {ip}"
            )
            return False

        try:

            if self.os_type == "Linux":
                success = self._block_linux(ip)

            elif self.os_type == "Windows":
                success = self._block_windows(ip)

            else:
                self.logger.warning(
                    f"Unsupported operating system: {self.os_type}"
                )
                return False

            if success:
                self.blocked_ips.add(ip)
                self.logger.log_block(ip)

            return success

        except Exception as error:

            self.logger.error(
                f"Firewall exception: {error}"
            )

            self.logger.log_error(
                f"Firewall exception for {ip}: {error}"
            )

            return False

    # --------------------------------------------------
    # Linux
    # --------------------------------------------------

    def _block_linux(self, ip: str) -> bool:

        # UFW installed?
        if shutil.which("ufw"):

            command = [
                "ufw",
                "deny",
                "from",
                ip
            ]

        # fallback -> iptables
        elif shutil.which("iptables"):

            command = [
                "iptables",
                "-A",
                "INPUT",
                "-s",
                ip,
                "-j",
                "DROP"
            ]

        else:

            self.logger.warning(
                "No supported Linux firewall found."
            )

            return False

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0

    # --------------------------------------------------
    # Windows
    # --------------------------------------------------

    def _block_windows(self, ip: str) -> bool:

        command = [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name=ZERGUZ_BLOCK_{ip}",
            "dir=in",
            "action=block",
            f"remoteip={ip}"
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def is_blocked(self, ip: str) -> bool:
        """
        Checks whether an IP has already been blocked.
        """

        return ip in self.blocked_ips
