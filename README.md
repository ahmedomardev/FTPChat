# FTPChat

### _Lightweight, End-to-End Encrypted FTP-Based Messaging Protocol_

---

## ⚡ Overview

**FTPChat** is a fast, lightweight, and end-to-end encrypted messaging application implemented in Python. It facilitates secure real-time communication by reading and writing structured payloads to a shared text file hosted on an FTP/FTPS/SFTP server.

Designed to operate seamlessly in restricted or legacy environments, FTPChat can run on low-power USB-enabled routers, remote servers, or air-gapped networks where traditional chat infrastructure cannot be deployed.

---

## 🔥 Key Features (v2.3)

- **🔐 End-to-End Encryption:** Messages are protected using `PBKDF2-SHA256` key derivation, `Fernet` symmetric encryption, and `zlib` compression to minimize bandwidth.
- **📱 True Cross-Platform UI:** Fully rebuilt with **Flet (Flutter)**, offering native desktop performance alongside a dedicated **Android mobile experience**.
- **🔄 Adaptive Transport Fallback:** Automatic connection sequence (`SFTP` ➔ `FTPS` ➔ `FTP`) guarantees delivery across varying network configurations.
- **⚡ High-Efficiency Syncing:** Uses line-count and byte-offset reading to fetch only newly posted messages, dramatically cutting down data usage.
- **📂 Saved Setup Profiles:** Save, edit, and delete multiple FTP configurations on the fly with per-setup notification controls.
- **🧵 Non-Blocking Architecture:** Fully threaded background send/receive loops keep the user interface smooth and responsive during file I/O.
- **🎯 Minimal Infrastructure:** Requires zero database setup—just any basic file transfer server.

---

## 📜 Protocol & Message Format

Messages are appended to a shared ledger file on the server. Each record consists of a **timestamp**, **sender identification**, and an **encrypted payload**:

$$\text{Message Record} = \text{Timestamp} \ \vert \ \text{Username} \ \vert \ \text{Base64}(\text{Encrypted Payload})$$

> [!NOTE]
> For servers without native `APPEND` command support, FTPChat automatically utilizes atomic lock-and-write fallbacks to prevent race conditions during simultaneous posts.

---

## 🚀 Installation & Setup

### Option 1: Native Binaries (Recommended)

Download the pre-compiled packages directly from [GitHub Releases](https://github.com/ahmedomardev/FTPChat/releases):

- 🖥️ **Windows:** Download `FTPChat.exe`
- 📱 **Android:** Download and install `FTPChat.apk`

---

### Option 2: Run from Source

#### Prerequisites

- **Python:** 3.8 or higher
- **Dependencies:** Install requirements via `pip`

```bash
# Clone repository
git clone https://github.com/ahmedomardev/FTPChat.git
cd FTPChat

# Install dependencies
pip install -r requirements.txt

# Launch application
python ftpchat.py

```

---

## 🛠️ Usage Workflow

| Step  | Action                 | Description                                                                                                                    |
| ----- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **1** | **Prepare FTP Server** | Use a local router FTP, dedicated server, or free cloud service like [SFTPCloud©](https://sftpcloud.io/tools/free-ftp-server). |
| **2** | **Configure Session**  | Open **Setup** and enter host, port, credentials, target chat filename, and shared encryption key.                             |
| **3** | **Start Chatting**     | Pick a display username and begin exchanging end-to-end encrypted messages instantly!                                          |

---

## 🖥️ System Requirements

| Platform          | Requirements                                     |
| ----------------- | ------------------------------------------------ |
| **Windows**       | Windows 10 / 11                                  |
| **Android**       | Android 8.0 (API level 26) or higher             |
| **Python Source** | Python 3.8+ (`flet`, `cryptography`, `paramiko`) |
| **Server**        | Any standard FTP, FTPS, or SFTP server           |

---

## 🚀 Deployment Scenarios

- **Local Area Networks:** Turn any USB-equipped home router into a private office chat server.
- **Air-Gapped & Restricted Nets:** Deploy over isolated FTP storage endpoints.
- **Low-Bandwidth Operations:** Compression and delta syncing allow operation over weak cellular or satellite links.

---

## 🛠️ Built With

- **Languages & Core:** Python 3, Dart (Flutter)
- **UI Engine:** Flet Framework
- **IDE & Tools:** VS Code, Git, Android SDK / Toolchain

---

## 📄 License & Terms

Copyright © **Ahmed Omar Saad**. All rights reserved.

Permission is hereby granted to use, copy, and distribute this software for non-commercial purposes under the following terms:

- **Commercial Use:** Requires explicit prior written authorization from the author.
- **Relicensing:** The author reserves the right to modify, restrict, or relicense the source code and protocol specification at any time.
- **Attribution:** The above copyright notice and this permission notice must be included in all copies.

_THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND._

---

## 📬 Contact & Links

- 📧 **Email:** [ahmedomardev@outlook.com](https://www.google.com/search?q=mailto%3Aahmedomardev%40outlook.com)
- 🐙 **GitHub:** [ahmedomardev/FTPChat](https://github.com/ahmedomardev/FTPChat)
- 🌐 **Website:** [ahmed-omar-software-projects.mydurable.com](https://www.google.com/search?q=https://ahmed-omar-software-projects.mydurable.com)
