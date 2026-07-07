import time

from core.banner import ZerguzBanner
from core.logger import ZerguzLogger
from core.firewall import ZerguzFirewallManager
from integrations.webhook import ZerguzWebhookNotifier
from network.connection_handler import ZerguzConnectionHandler
from network.honeypot import ZerguzHoneypotServer
from network.upnp_manager import ZerguzUPnPManager
from network.scan_sniffer import ZerguzScanSniffer


class ZerguzEngine:

    def __init__(self) -> None:
        self.logger = ZerguzLogger()
        self.firewall = ZerguzFirewallManager(self.logger)
        self.webhook = ZerguzWebhookNotifier(logger=self.logger, discord_webhook_url="")
        self.connection_handler = ZerguzConnectionHandler(
            logger=self.logger,
            firewall=self.firewall,
            webhook=self.webhook
        )
        self.upnp_manager = ZerguzUPnPManager(self.logger)

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
            ),
            ZerguzHoneypotServer(
                host="0.0.0.0",
                port=21,
                logger=self.logger,
                connection_handler=self.connection_handler
            )
        ]

        self.scan_sniffer = ZerguzScanSniffer(
            logger=self.logger,
            ports=[service.port for service in self.services]
        )

    def run(self) -> None:
        try:
            ZerguzBanner.show()
            self.logger.info("Initializing Zerguz Engine...")
            self.upnp_manager.setup()

            for service in self.services:
                service.start()

            self.scan_sniffer.start()

            self.logger.success("Zerguz Engine started successfully.")
            self.logger.success("SSH Honeypot -> TCP/2222")
            self.logger.success("HTTP Honeypot -> TCP/8080")
            self.logger.success("FTP Honeypot -> TCP/21")

            self.logger.info("Press CTRL+C to stop.")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as error:
            self.logger.error(f"Engine crashed: {error}")
            self.logger.log_error(f"Engine crashed: {error}")
            self.shutdown()

    def shutdown(self) -> None:
        self.logger.warning("Shutting down Zerguz...")
        self.scan_sniffer.stop()
        for service in self.services:
            service.stop()
        self.upnp_manager.cleanup()
        self.logger.success("Zerguz stopped successfully.")
        raise SystemExit(0)
