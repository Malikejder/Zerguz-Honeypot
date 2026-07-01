# network/honeypot.py

import socket
import threading
import time

from core.logger import ZerguzLogger
from network.connection_handler import ZerguzConnectionHandler


class ZerguzHoneypotServer:
    """
    Generic TCP honeypot server.

    Responsible for:
        - Opening listening sockets
        - Accepting incoming connections
        - Creating worker threads
        - Keeping service alive
    """

    BACKLOG = 100
    BUFFER_SIZE = 4096

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

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def start(self) -> None:
        """
        Starts the honeypot service in a daemon thread.
        """

        if self.is_running:
            return

        self.is_running = True

        thread = threading.Thread(
            target=self._listen,
            daemon=True,
            name=f"Zerguz-{self.port}"
        )

        thread.start()

    def stop(self) -> None:
        """
        Gracefully stops the honeypot service.
        """

        self.is_running = False

        try:
            if self.server_socket:
                self.server_socket.close()

            self.logger.warning(
                f"Honeypot on port {self.port} stopped."
            )

        except Exception as error:

            self.logger.error(
                f"Stop error on port "
                f"{self.port}: {error}"
            )

    # --------------------------------------------------
    # Internal Methods
    # --------------------------------------------------

    def _listen(self) -> None:
        """
        Main listening loop.
        """

        while self.is_running:

            try:

                self.server_socket = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                self.server_socket.setsockopt(
                    socket.SOL_SOCKET,
                    socket.SO_REUSEADDR,
                    1
                )

                self.server_socket.bind(
                    (self.host, self.port)
                )

                self.server_socket.listen(
                    self.BACKLOG
                )

                self.logger.success(
                    f"Zerguz listening on "
                    f"{self.host}:{self.port}"
                )

                while self.is_running:

                    try:

                        client_socket, client_address = (
                            self.server_socket.accept()
                        )

                        self.logger.info(
                            f"Incoming connection "
                            f"{client_address[0]}:"
                            f"{client_address[1]}"
                        )

                        worker = threading.Thread(
                            target=self.connection_handler.handle,
                            args=(
                                client_socket,
                                client_address,
                                self.port
                            ),
                            daemon=True
                        )

                        worker.start()

                    except OSError:
                        break

                    except Exception as error:

                        self.logger.error(
                            f"Accept error "
                            f"on port {self.port}: {error}"
                        )

            except Exception as error:

                self.logger.error(
                    f"Listener crashed on "
                    f"port {self.port}: {error}"
                )

                time.sleep(5)

            finally:

                try:
                    if self.server_socket:
                        self.server_socket.close()
                except Exception:
                    pass
