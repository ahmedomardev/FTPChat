# FTPChat

## Encrypted FTP-based Messaging Protocol

**Version: 1.7**  
**Type:** Custom Proprietary License  
**Author:** Ahmed Omar Saad  
**Contact:** <ahmedomardev@outlook.com>

---

## Overview

FTPChat is a lightweight, encrypted messaging protocol implemented entirely in Python. It facilitates secure communication by reading and writing messages to a shared file hosted on an FTP server.

FTPChat is specifically designed for deployment in legacy environments, including low-power routers equipped with USB and FTP capabilities. This makes it an ideal solution for resource-constrained scenarios or discreet operations.

---

## Key Features (v1.7)

- **PBKDF2 SHA-256 Encryption** with Fernet for robust payload security
- **File-based transport mechanism** utilizing FTP/FTPS fallback for maximum compatibility
- **Single `.py` file deployment** for simplicity and portability
- **Optimized for legacy hardware and low-power devices**
- **International chatting** via [SFTPCloud Tool](https://sftpcloud.io/tools/free-ftp-server)
- **Local LAN support** — set up your own FTP server
- **Threaded send/receive** — no UI freezing during FTP operations
- **Auto-refresh loop** with restart-safe scheduling
- **Modern GUI** built with CustomTkinter
- **Non-editable chat history** with scrollable view
- **Password-protected chats** with encryption key derivation
- **Message Compression** using zlib for reduced file sizes
- **Offset-based message fetching** to minimize bandwidth usage

---

## New Features in v1.7

- **Updated to CustomTkinter** for improved modern UI
- **Enhanced threading** for better performance
- **Improved error handling** and user feedback
- **Auto-scroll chat window** showing latest messages
- **Compression and encryption** pipeline for efficient data handling

---

## Protocol Operation

Messages are exchanged via a shared text file on an FTP server. Each message contains:

- Timestamp (YYYY-MM-DD HH:MM format)
- Username
- Encrypted content (Base64-encoded Fernet encryption with compression)

The protocol provides:

- Conflict-safe message writing (with fallback for servers not supporting APPEND)
- Encrypted message formatting
- Lightweight, file-based communication
- Automatic compression for reduced file sizes
- Offset-based reading to fetch only new messages

---

## Installation

**Option 1: Executable**

- Download `FtpChat.exe` for Windows 10/11 from [Releases](https://github.com/ahmedomardev/FTPChat/releases)

**Option 2: Python Source**

- Clone from [GitHub](https://github.com/ahmedomardev/FTPChat)
- Requires Python 3.8+ with dependencies: `cryptography`, `customtkinter`

Install dependencies via pip:

```
pip install cryptography customtkinter
```

---

## Usage Instructions

1. **Prepare FTP Server**
   - Set up an FTP server (local LAN or cloud-based)
   - Refer to `Documentation/Quick Start Guide (Making FTP Server).md` for local setup
   - Or use [SFTPCloud](https://sftpcloud.io/tools/free-ftp-server) for global access

2. **Run FTPChat**
   - Execute `FtpChat.exe` (Windows) or `python FtpChat.py` (MacOS or Linux)

3. **Configure Connection**
   - Click "Setup" to enter FTP host, username, password, chat file name, and encryption key
   - Encryption key is used for message encryption/decryption

4. **Start Chatting**
   - Enter username and type messages
   - Send messages using the "Send" button or Alt key
   - Messages auto-sync across all connected clients
   - Chat history is non-editable and read-only

---

## Requirements

1. For source code:
   - Python 3.8+
   - Dependencies: `cryptography`, `customtkinter`
2. For Exe:
   - Windows 10/11
3. For Both
   - FTP server access (local or remote)

---

## Deployment Scenarios

- **Local Network**: Set up FTP on a local server for team communication
- **Remote/Global**: Use cloud FTP services for worldwide access
- **Legacy Hardware**: Deploy on low-power routers with USB and FTP support
- **Offline Operations**: Messages sync only when FTP connection is available

---

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, and/or sublicense copies of the Software, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
- **Commercial use of this software requires prior written permission from the author.**
- **The author reserves the right to relicense this software as closed-source or commercial at any time.**
- All rights to the name “FTPChat” and its protocol specification are retained by Ahmed Omar Saad.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Notes: The author may offer separate commercial licenses for enterprise or closed-source use. Contact <ahmedomardev@outlook.com> for inquiries. This license applies to all source code, documentation, and protocol specifications included in the FTPChat project.

---

## Notes:

- The supplies folder is for the apps used in the app development.

---

## Support & Contact

- **Email:** [ahmedomardev@outlook.com](mailto:ahmedomardev@outlook.com)
- **GitHub:** [https://github.com/ahmedomardev/FTPChat](https://github.com/ahmedomardev/FTPChat)
- **Website:** [ahmed-omar-software-projects.mydurable.com](ahmed-omar-software-projects.mydurable.com)
