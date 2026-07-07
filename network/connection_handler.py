import socket
from datetime import datetime

from core.logger import ZerguzLogger
from core.firewall import ZerguzFirewallManager
from integrations.webhook import ZerguzWebhookNotifier


class ZerguzConnectionHandler:

    def __init__(
            self,
            logger: ZerguzLogger,
            firewall: ZerguzFirewallManager,
            webhook: ZerguzWebhookNotifier
    ) -> None:
        self.logger = logger
        self.firewall = firewall
        self.webhook = webhook

    def handle(self, client_socket: socket.socket, client_address: tuple, service_port: int) -> None:
        attacker_ip = client_address[0]
        try:
            client_socket.settimeout(10)

            # Önce banner gönder (FTP için önemli)
            if service_port == 21:
                client_socket.sendall(b"220 Zerguz FTP Server ready.\r\n")
            elif service_port == 2222:
                client_socket.sendall(b"SSH-2.0-OpenSSH_8.4p1 Ubuntu-5ubuntu1\r\n")
            elif service_port == 8080:
                client_socket.sendall(
                    b"HTTP/1.1 200 OK\r\n"
                    b"Server: Apache/2.4.41 (Ubuntu)\r\n"
                    b"Content-Type: text/html\r\n\r\n"
                    b"<html><head><title>Apache2 Ubuntu Default Page</title></head>"
                    b"<body><h1>It works!</h1></body></html>"
                )

            # Payload oku
            try:
                raw_data = client_socket.recv(4096)
                payload = raw_data.decode(errors="ignore").strip()
            except socket.timeout:
                payload = "No payload received"
            except Exception:
                payload = "Payload decode failed"

            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            self.logger.log_attack(attacker_ip, service_port)
            self.logger.log_info(
                f"[ZERGUZ PAYLOAD] TIME={timestamp} | "
                f"SRC={attacker_ip} | DST_PORT={service_port} | "
                f"PAYLOAD={payload[:300]}"
            )

            blocked = self.firewall.block_ip(attacker_ip)
            if blocked:
                self.webhook.send_attack_alert(attacker_ip, service_port)

        except Exception as error:
            self.logger.error(f"Connection handler exception: {error}")
            self.logger.log_error(f"Connection handler exception: {error}")

        finally:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                client_socket.close()
            except Exception:
                pass
