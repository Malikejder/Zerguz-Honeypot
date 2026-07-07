import threading

from core.logger import ZerguzLogger

try:
    from scapy.all import sniff, TCP, IP
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class ZerguzScanSniffer:
    """
    Uygulama seviyesindeki (accept/connect tabanlı) loglamadan bağımsız olarak
    çalışır. Honeypot portlarına gelen HER paketi (SYN scan, connect scan,
    FIN/NULL/Xmas scan, ACK scan vb.) TCP el sıkışması tamamlansa da
    tamamlanmasa da yakalar ve loglar.

    nmap gibi araçlar varsayılan olarak (root ile) SYN scan (-sS) kullanır.
    Bu tarama türünde uygulama seviyesinde accept() asla tetiklenmediği için
    normal honeypot loglaması bu taramaları göremez. Bu sınıf, ham soket
    (raw socket) seviyesinde dinleme yaparak bu boşluğu kapatır.
    """

    # TCP flag bitleri -> insan tarafından okunabilir isim
    FLAG_NAMES = {
        "S": "SYN",
        "SA": "SYN-ACK",
        "A": "ACK",
        "F": "FIN",
        "FA": "FIN-ACK",
        "R": "RST",
        "RA": "RST-ACK",
        "P": "PSH",
        "PA": "PSH-ACK",
        "FPU": "FIN-PSH-URG (Xmas Scan)",
        "": "NULL (Null Scan)",
        "U": "URG",
    }

    def __init__(self, logger: ZerguzLogger, ports: list, interface: str = None) -> None:
        self.logger = logger
        self.ports = set(ports)
        self.interface = interface
        self._thread = None
        self._stop_event = threading.Event()
        # Aynı IP/port/flag kombinasyonunu saniyede defalarca loglamamak
        # için basit bir tekrar bastırma (dedup) mekanizması.
        self._last_seen = {}
        self._dedup_window = 2.0  # saniye

    def start(self) -> None:
        if not SCAPY_AVAILABLE:
            self.logger.error(
                "scapy bulunamadı. 'pip install scapy' ile kurun. "
                "Paket seviyeli tarama tespiti devre dışı."
            )
            self.logger.log_error("scapy not installed; packet-level scan detection disabled.")
            return

        self._thread = threading.Thread(target=self._run, daemon=True, name="Zerguz-ScanSniffer")
        self._thread.start()
        self.logger.success(
            f"Packet-level scan sniffer started for ports: {sorted(self.ports)}"
        )

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        port_filter = " or ".join(f"port {p}" for p in self.ports)
        bpf_filter = f"tcp and ({port_filter})"

        try:
            sniff(
                filter=bpf_filter,
                prn=self._handle_packet,
                store=False,
                stop_filter=lambda pkt: self._stop_event.is_set(),
                iface=self.interface,
            )
        except PermissionError:
            self.logger.error(
                "Paket dinleyici için yeterli izin yok. Programı root/sudo ile çalıştırın "
                "(ham soket erişimi CAP_NET_RAW gerektirir)."
            )
            self.logger.log_error("Scan sniffer permission denied; needs root/CAP_NET_RAW.")
        except Exception as error:
            self.logger.error(f"Scan sniffer crashed: {error}")
            self.logger.log_error(f"Scan sniffer crashed: {error}")

    def _handle_packet(self, packet) -> None:
        try:
            if IP not in packet or TCP not in packet:
                return

            dst_port = packet[TCP].dport
            if dst_port not in self.ports:
                return

            src_ip = packet[IP].src
            flags = packet.sprintf("%TCP.flags%")
            flag_label = self.FLAG_NAMES.get(flags, flags or "NULL")

            dedup_key = (src_ip, dst_port, flags)
            now = threading.get_ident() and __import__("time").time()
            last = self._last_seen.get(dedup_key)
            if last is not None and (now - last) < self._dedup_window:
                return
            self._last_seen[dedup_key] = now

            message = (
                f"[ZERGUZ SCAN] SRC={src_ip} | DST_PORT={dst_port} | "
                f"FLAGS={flag_label} ({flags})"
            )
            self.logger.warning(f"Scan/packet detected -> {src_ip}:{dst_port} [{flag_label}]")
            self.logger.log_warning(message)

        except Exception as error:
            self.logger.error(f"Packet handling error: {error}")
