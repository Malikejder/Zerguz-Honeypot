# integrations/webhook.py

import requests

from core.logger import ZerguzLogger


class ZerguzWebhookNotifier:
    """
    Sends security alerts to external platforms.

    Currently supported:
        - Discord Webhook

    Future:
        - Telegram
        - Slack
        - Microsoft Teams
    """

    def __init__(
            self,
            logger: ZerguzLogger,
            discord_webhook_url: str = ""
    ) -> None:

        self.logger = logger
        self.discord_webhook_url = discord_webhook_url

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def send_attack_alert(
            self,
            ip: str,
            port: int
    ) -> None:

        if not self.discord_webhook_url:
            return

        payload = {
            "content":
                "🚨 **[ZERGUZ DETECT]**\n\n"
                f"**Attack Detected!**\n"
                f"**Source IP:** `{ip}`\n"
                f"**Target Port:** `{port}`\n\n"
                "🛡️ IP has been blocked automatically."
        }

        try:

            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code in (200, 204):

                self.logger.success(
                    f"Webhook alert sent for {ip}"
                )

                self.logger.log_info(
                    f"Webhook notification sent -> {ip}"
                )

            else:

                self.logger.warning(
                    f"Webhook failed "
                    f"(HTTP {response.status_code})"
                )

        except requests.exceptions.Timeout:

            self.logger.error(
                "Webhook timeout occurred."
            )

        except requests.exceptions.ConnectionError:

            self.logger.error(
                "Webhook connection failed."
            )

        except Exception as error:

            self.logger.error(
                f"Webhook exception: {error}"
            )

            self.logger.log_error(
                f"Webhook exception: {error}"
            )
