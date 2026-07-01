# network/connection_handler.py

import socket
from datetime import datetime

from core.logger import ZerguzLogger
from core.firewall import ZerguzFirewallManager
from integrations.webhook import ZerguzWebhookNotifier


class ZerguzConnectionHandler:
    """
    Handles incoming connections for all honeypot services.
    """

    def __init__(
            self,
            logger: ZerguzLogger,
            firewall: ZerguzFirewallManager,
            webhook: ZerguzWebhookNotifier
    ) -> None:

        self.logger = logger
        self.firewall = firewall
        self.webhook = webhook

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def handle(
            self,
            client_socket: socket.socket,
            client_address: tuple,
            service_port: int
    ) -> None:
        """
        Main connection processing routine.
        """

        attacker_ip = client_address[0]

        try:

            client_socket.settimeout(5)

            # Try to capture incoming data
            try:
                raw_data = client_socket.recv(4096)

                payload = (
                    raw_data.decode(
                        errors="ignore"
                    ).strip()
                )

            except socket.timeout:
                payload = "No payload received"

            except Exception:
                payload = "Payload decode failed"

            timestamp = datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )

            # Console + File Logging
            self.logger.log_attack(
                attacker_ip,
                service_port
            )

            self.logger.log_info(
                f"[ZERGUZ PAYLOAD] "
                f"TIME={timestamp} | "
                f"SRC={attacker_ip} | "
                f"DST_PORT={service_port} | "
                f"PAYLOAD={payload[:300]}"
            )

            # Active Defense
            blocked = self.firewall.block_ip(
                attacker_ip
            )

            # Webhook Alert
            if blocked:

                self.webhook.send_attack_alert(
                    attacker_ip,
                    service_port
                )

            # --------------------------------------------------
            # Fake Service Responses
            # --------------------------------------------------

            if service_port == 2222:

                fake_ssh_banner = (
                    b"SSH-2.0-OpenSSH_8.4p1 Ubuntu-5ubuntu1\r\n"
                )

                client_socket.sendall(
                    fake_ssh_banner
                )

            elif service_port == 8080:

                fake_http_response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Server: Apache/2.4.41 (Ubuntu)\r\n"
                    "Content-Type: text/html\r\n\r\n"
                    "<html>"
                    "<head><title>Apache2 Ubuntu Default Page</title></head>"
                    "<body><h1>It works!</h1></body>"
                    "</html>"
                )

                client_socket.sendall(
                    fake_http_response.encode()
                )

        except Exception as error:

            self.logger.error(
                f"Connection handler exception: {error}"
            )

            self.logger.log_error(
                f"Connection handler exception: {error}"
            )

        finally:

            try:
                client_socket.shutdown(
                    socket.SHUT_RDWR
                )
            except Exception:
                pass

            try:
                client_socket.close()
            except Exception:
                pass
