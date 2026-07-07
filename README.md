# 🛡️ Zerguz Honeypot

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge\&logo=linux\&logoColor=black)
![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</p>

A lightweight and modular Python-based honeypot developed for cybersecurity learning, Blue Team practices and SOC Analyst portfolio projects.

---

# 📖 About

Zerguz Honeypot is a modular honeypot application that listens for incoming network connections, records connection events and demonstrates the core concepts behind network monitoring and defensive security.

This project was developed to strengthen my understanding of:

* Socket Programming
* Network Security
* Python Development
* Security Logging
* Blue Team Operations
* SOC Analyst Workflows

The project emphasizes clean code, modular architecture and maintainability.

---

# ✨ Features

* Modular project architecture
* TCP Honeypot Server
* Multithreaded connection handling
* Connection logging
* **Packet-level scan detection** (catches SYN, FIN, NULL, Xmas and other scan types — even when no full TCP handshake is completed)
* Colored console output
* Firewall management
* UPnP port management
* Webhook notification support
* Graceful shutdown
* Lightweight design

---

# 🏗️ Architecture

```text
                    +----------------+
                    |    main.py     |
                    +--------+-------+
                             |
                             ▼
                     Zerguz Engine
                             |
        +---------+----------+----------+----------------+
        |         |                     |                |
        ▼         ▼                     ▼                ▼
     Banner   Firewall          Honeypot Server     Scan Sniffer
                                      |               (raw socket)
                                      ▼                    |
                           Connection Handler              |
                                      |                    |
                                      ▼                    ▼
                                   Logger  <----------------
```

---

# 📁 Project Structure

```text
Zerguz/
│
├── core/
│   ├── __init__.py
│   ├── banner.py
│   ├── engine.py
│   ├── firewall.py
│   └── logger.py
│
├── network/
│   ├── __init__.py
│   ├── connection_handler.py
│   ├── honeypot.py
│   ├── scan_sniffer.py
│   └── upnp_manager.py
│
├── integrations/
│   ├── __init__.py
│   └── webhook.py
│
├── requirements.txt
└── main.py
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Malikejder/Zerguz.git
cd Zerguz
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
sudo python3 main.py
```

> **Note:** `sudo`/root privileges are required. The application binds to low honeypot ports (21, 2222) and the scan sniffer needs `CAP_NET_RAW` for raw socket packet capture.

---

# 🧰 Technologies

* Python
* Socket Programming
* Multithreading
* Raw Sockets / Packet Sniffing (Scapy)
* Linux Networking
* Firewall Management
* TCP/IP
* Webhooks

---

# 🔄 Application Flow

```text
Incoming Packet / Connection
        │
        ├──► Full TCP Connection (e.g. nmap -sT, real service probes)
        │         │
        │         ▼
        │    Honeypot Listener ──► Connection Handler ──► Logger
        │
        └──► Raw Packet, handshake not completed (e.g. nmap -sS SYN scan,
              FIN/NULL/Xmas scans)
                  │
                  ▼
              Scan Sniffer ──► Logger
                                  │
                                  ├── Console Output
                                  ├── zerguz_alerts.log
                                  └── Webhook Notification
```

---

# 🕵️ Scan Detection Details

Standard honeypots that only log on `accept()` miss stealth scans, because tools like `nmap` default to a **SYN scan (`-sS`)** when run as root. In a SYN scan the kernel replies with SYN-ACK, but the scanner never completes the handshake (it sends RST instead) — so the application-level listener never sees the connection.

To close this gap, Zerguz runs an independent **packet-level sniffer** (`network/scan_sniffer.py`) using raw sockets via `scapy`. It inspects every TCP packet destined for the monitored honeypot ports and logs it regardless of TCP flags, including:

| Scan Type          | nmap Flag | Detected |
|---------------------|-----------|----------|
| Connect Scan         | `-sT`     | ✅ |
| SYN (Stealth) Scan   | `-sS`     | ✅ |
| FIN Scan             | `-sF`     | ✅ |
| NULL Scan            | `-sN`     | ✅ |
| Xmas Scan            | `-sX`     | ✅ |
| ACK Scan             | `-sA`     | ✅ |

A short deduplication window prevents a single scan from flooding the log file with duplicate entries for the same source IP / port / flag combination.

---

# 🎯 Purpose

This project is intended for:

* Cybersecurity learning
* Blue Team practice
* SOC Analyst portfolio
* Python network programming
* Understanding honeypot fundamentals

---

# 👨‍💻 Author

**Malikejder Durgun**

Cybersecurity Enthusiast | SOC Analyst Candidate

GitHub: https://github.com/Malikejder

---

# 📄 License

This project is licensed under the MIT License.

---

# ⚠️ Disclaimer

This project is provided for educational and defensive cybersecurity purposes only.

Do not deploy or use this software against systems without proper authorization.
