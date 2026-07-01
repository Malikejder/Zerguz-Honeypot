# core/engine.py

import time

from core.banner import ZerguzBanner
from core.logger import ZerguzLogger
from core.firewall import ZerguzFirewallManager

from integrations.webhook import ZerguzWebhookNotifier

from network.connection_handler import ZerguzConnectionHandler
from network.honeypot import ZerguzHoneypotServer
from network.upnp_manager import ZerguzUPnPManager


class ZerguzEngine:
    """
    Main orchestration engine for Zerguz.

    Responsible for:
        - Initializing components
        - Starting honeypot services
        - Managing application lifecycle
    """

    def __init__(self) -> None:

        # Core Components
        self.logger = ZerguzLogger()
        self.firewall = ZerguzFirewallManager(
            self.logger
        )

        # Discord Webhook URL
        self.webhook = ZerguzWebhookNotifier(
            logger=self.logger,
            discord_webhook_url=""
        )

        # Connection Handler
        self.connection_handler = (
            ZerguzConnectionHandler(
                logger=self.logger,
                firewall=self.firewall,
                webhook=self.webhook
            )
        )

        # UPnP Manager
        self.upnp_manager = ZerguzUPnPManager(
            self.logger
        )

        # Honeypot Services
        self.services = [

            ZerguzHoneypotServer(
                host="0.0.0.0",
                port=2222,
                logger=self.logger,
                connection_handler=self.connection_handler
            ),

            ZerguzHoneypotServer(
                host="0.0.0.0",
                port=8080,
                logger=self.logger,
                connection_handler=self.connection_handler
            )
        ]

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def run(self) -> None:
        """
        Starts the entire Zerguz platform.
        """

        try:

            ZerguzBanner.show()

            self.logger.info(
                "Initializing Zerguz Engine..."
            )

            # Try automatic port forwarding
            self.upnp_manager.setup()

            # Start Honeypots
            for service in self.services:
                service.start()

            self.logger.success(
                "Zerguz Engine started successfully."
            )

            self.logger.success(
                "SSH Honeypot -> TCP/2222"
            )

            self.logger.success(
                "HTTP Honeypot -> TCP/8080"
            )

            self.logger.info(
                "Press CTRL+C to stop."
            )

            while True:
                time.sleep(1)

        except KeyboardInterrupt:

            self.shutdown()

        except Exception as error:

            self.logger.error(
                f"Engine crashed: {error}"
            )

            self.logger.log_error(
                f"Engine crashed: {error}"
            )

            self.shutdown()

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def shutdown(self) -> None:
        """
        Gracefully shuts down all services.
        """

        self.logger.warning(
            "Shutting down Zerguz..."
        )

        # Stop honeypots
        for service in self.services:
            service.stop()

        # Remove UPnP mappings
        self.upnp_manager.cleanup()

        self.logger.success(
            "Zerguz stopped successfully."
        )

        raise SystemExit(0)

