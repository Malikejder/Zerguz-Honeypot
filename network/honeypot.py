import socket
import threading
import time

from core.logger import ZerguzLogger
from network.connection_handler import ZerguzConnectionHandler


class ZerguzHoneypotServer:

    BACKLOG = 5

    def __init__(
            self,
            host: str,
            port: int,
            logger: ZerguzLogger,
            connection_handler: ZerguzConnectionHandler
    ) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.connection_handler = connection_handler
        self.server_socket = None
        self.is_running = False

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        thread = threading.Thread(target=self._listen, daemon=True, name=f"Zerguz-{self.port}")
        thread.start()

    def stop(self) -> None:
        self.is_running = False
        try:
            if self.server_socket:
                self.server_socket.close()
            self.logger.warning(f"Honeypot on port {self.port} stopped.")
        except Exception as error:
            self.logger.error(f"Stop error on port {self.port}: {error}")

    def _listen(self) -> None:
        while self.is_running:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # TCP_NODELAY — yanıtların gecikmesiz gitmesini sağlar
                self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(self.BACKLOG)
                self.server_socket.settimeout(1.0)  # timeout ile is_running kontrolü

                self.logger.success(f"Zerguz listening on {self.host}:{self.port}")

                while self.is_running:
                    try:
                        client_socket, client_address = self.server_socket.accept()
                        self.logger.info(f"Incoming connection {client_address[0]}:{client_address[1]}")
                        worker = threading.Thread(
                            target=self.connection_handler.handle,
                            args=(client_socket, client_address, self.port),
                            daemon=True
                        )
                        worker.start()
                    except socket.timeout:
                        continue
                    except OSError:
                        break
                    except Exception as error:
                        self.logger.error(f"Accept error on port {self.port}: {error}")

            except Exception as error:
                self.logger.error(f"Listener crashed on port {self.port}: {error}")
                time.sleep(3)

            finally:
                try:
                    if self.server_socket:
                        self.server_socket.close()
                except Exception:
                    pass
