# network/upnp_manager.py

import miniupnpc

from core.logger import ZerguzLogger


class ZerguzUPnPManager:
    """
    Automatically configures port forwarding
    using UPnP compatible routers.
    """

    PORTS = [2222, 8080]

    def __init__(
            self,
            logger: ZerguzLogger
    ) -> None:

        self.logger = logger
        self.upnp = miniupnpc.UPnP()

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def setup(self) -> None:
        """
        Discovers UPnP devices and creates
        required port mappings.
        """

        try:

            self.logger.info(
                "Searching for UPnP devices..."
            )

            discovered = self.upnp.discover()

            if discovered == 0:

                self.logger.warning(
                    "No UPnP-enabled router found."
                )

                return

            self.upnp.selectigd()

            local_ip = self.upnp.lanaddr
            public_ip = self.upnp.externalipaddress()

            self.logger.success(
                f"Router discovered."
            )

            self.logger.success(
                f"Local IP  : {local_ip}"
            )

            self.logger.success(
                f"Public IP : {public_ip}"
            )

            for port in self.PORTS:

                self._map_port(
                    local_ip,
                    port
                )

        except Exception as error:

            self.logger.error(
                f"UPnP setup failed: {error}"
            )

            self.logger.log_error(
                f"UPnP setup failed: {error}"
            )

    def cleanup(self) -> None:
        """
        Removes port mappings during shutdown.
        """

        try:

            for port in self.PORTS:

                self.upnp.deleteportmapping(
                    port,
                    "TCP"
                )

                self.logger.info(
                    f"Port mapping removed: {port}"
                )

        except Exception:
            pass

    # --------------------------------------------------
    # Internal Methods
    # --------------------------------------------------

    def _map_port(
            self,
            local_ip: str,
            port: int
    ) -> None:

        try:

            existing = (
                self.upnp.getspecificportmapping(
                    port,
                    "TCP"
                )
            )

            if existing:

                self.logger.warning(
                    f"Port {port} already mapped."
                )

                return

            result = self.upnp.addportmapping(
                port,
                "TCP",
                local_ip,
                port,
                f"Zerguz Honeypot Port {port}",
                ""
            )

            if result:

                self.logger.success(
                    f"UPnP mapped TCP/{port}"
                )

                self.logger.log_info(
                    f"UPnP mapping successful "
                    f"for port {port}"
                )

            else:

                self.logger.warning(
                    f"Failed to map TCP/{port}"
                )

        except Exception as error:

            self.logger.error(
                f"Port mapping error "
                f"({port}): {error}"
            )

            self.logger.log_error(
                f"UPnP mapping error "
                f"({port}): {error}"
            )
