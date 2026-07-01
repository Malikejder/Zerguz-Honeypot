# core/banner.py

from colorama import Fore, Style, init

init(autoreset=True)


class ZerguzBanner:
    """
    Displays the official Zerguz startup banner.
    """

    @staticmethod
    def show() -> None:

        banner = f"""
{Fore.RED}
███████╗███████╗██████╗  ██████╗ ██╗   ██╗███████╗
╚══███╔╝██╔════╝██╔══██╗██╔════╝ ██║   ██║╚══███╔╝
  ███╔╝ █████╗  ██████╔╝██║  ███╗██║   ██║  ███╔╝
 ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██║   ██║ ███╔╝
███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝███████╗
╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝

██╗  ██╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗ ████████╗
██║  ██║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
███████║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ ██████╔╝██║   ██║   ██║
██╔══██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  ██╔═══╝ ██║   ██║   ██║
██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ██║     ╚██████╔╝   ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝      ╚═════╝    ╚═╝

{Fore.CYAN}
══════════════════════════════════════════════════════════════
                Zerguz Honeypot & Alerting Tool
                         Version: 1.0.0
══════════════════════════════════════════════════════════════

{Fore.YELLOW}Author  : Malikejder Durgun
{Fore.YELLOW}Framework : Zerguz Active Defense Platform

{Fore.GREEN}[+] Initializing Security Components...
{Style.RESET_ALL}
"""

        print(banner)
