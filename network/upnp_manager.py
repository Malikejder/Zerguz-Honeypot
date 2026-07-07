from core.logger import ZerguzLogger


class ZerguzUPnPManager:

    def __init__(self, logger: ZerguzLogger) -> None:
        self.logger = logger

    def setup(self) -> None:
        self.logger.info("UPnP port forwarding skipped (optional).")

    def cleanup(self) -> None:
        pass
