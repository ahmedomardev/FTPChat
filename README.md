# FTPChat

## Encrypted FTP-based Messaging Protocol

**Version 1.6 — February 2026**  
**Author:** Ahmed Omar Saad  
**Contact:** <ahmedomardev@outlook.com>

---

## Overview

FTPChat is a lightweight, encrypted messaging protocol implemented entirely in Python. It facilitates secure communication by reading and writing messages to a shared file hosted on an FTP server.

FTPChat is specifically designed for deployment in legacy environments, including low-power routers equipped with USB and FTP capabilities. This makes it an ideal solution for resource-constrained scenarios or discreet operations.

---

## Key Features (v1.6)

- **PBKDF2 SHA-256 Encryption** with Fernet for robust payload security
- **File-based transport mechanism** utilizing FTP/FTPS fallback for maximum compatibility
- **Single `.py` file deployment** for simplicity and portability
- **Optimized for legacy hardware and low-power devices**
- **International chatting** via [SFTPCloud Tool](https://sftpcloud.io/tools/free-ftp-server)
- **Local LAN support** — set up your own FTP server
- **Threaded send/receive** — no UI freezing during FTP operations
- **Auto-refresh loop** with restart-safe scheduling
- **Modern GUI** built with ttkbootstrap
- **Non-editable chat history** with scrollable view
- **Password-protected chats** with encryption key derivation

---

## New Features in v1.6

- **PBKDF2 SHA-256 Encryption** with Fernet for enhanced security
- **Threaded FTP I/O** for non-blocking message operations
- **FTP/FTPS Fallback** for maximum compatibility
- **Modern ttkbootstrap UI** with improved styling
- **Auto-refresh Loop** with restart-safe scheduling
- **Message Compression** for reduced file sizes
- **Auto-Scroll Chat Window** showing latest messages
- **Password-Protected Sessions** with key derivation

---

## Protocol Operation

Messages are exchanged via a shared text file on an FTP server. Each message contains:

- Timestamp (YYYY-MM-DD HH:MM format)
- Username
- Encrypted content (Base64-encoded Fernet encryption with compression)

The protocol provides:

- Conflict-safe message writing
- Encrypted message formatting
- Lightweight, file-based communication
- Automatic compression for reduced file sizes

---

## Installation

**Option 1: Executable**

- Download `FtpChat.exe` for Windows 10/11 from [Releases](https://github.com/ahmedomar2014/FTPChat/releases)

**Option 2: Python Source**

- Clone from [GitHub](https://github.com/ahmedomar2014/FTPChat)
- Requires Python 3.8+ with dependencies: `cryptography`, `ttkbootstrap`

---

## Usage Instructions

1. **Prepare FTP Server**
   - Set up an FTP server (local LAN or cloud-based)
   - Refer to `Documentation/Quick Start Guide (Making FTP Server).md` for local setup
   - Or use [SFTPCloud](https://sftpcloud.io/tools/free-ftp-server) for global access

2. **Run FTPChat**
   - Execute `FtpChat.exe` (Windows) or `python FtpChat.py` (MacOS or Linux)

3. **Configure Connection**
   - Enter FTP host, username, and password
   - Set encryption password (for message encryption)
   - Choose a chat file name

4. **Start Chatting**
   - Type messages and send via the UI
   - Messages auto-sync across all connected clients
   - Chat history is non-editable and read-only

---

## Requirements

- Windows 10/11 for FTPChat.exe or MacOS or linux for ftpchat.py
- At least 70Mb of free disk space

---

## Deployment Scenarios

- **Local Network**: Set up FTP on a local server for team communication
- **Remote/Global**: Use cloud FTP services for worldwide access
- **Legacy Hardware**: Deploy on low-power routers with USB and FTP support
- **Offline Operations**: Messages sync only when FTP connection is available

---

## License

FTPChat is distributed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

**Key Terms:**

- ✓ Free for personal and educational use
- ✓ Modification and distribution allowed (with attribution)
- ✗ **Commercial use is strictly prohibited** without written permission
- ✗ **Closed-source use requires separate license agreement**

**FTPChat © 2025 by Ahmed Omar Saad is licensed under CC BY-NC-SA 4.0**  
To view a copy of this license, visit [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

## Warranty Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Commercial Licensing

The author may offer separate commercial licenses for enterprise or closed-source use. Contact [ahmedomardev@outlook.com](mailto:ahmedomardev@outlook.com) for licensing inquiries.

This license applies to all source code, documentation, and project specifications included in the FTPChat project.

---

## Support & Contact

- **Email:** [ahmedomardev@outlook.com](mailto:ahmedomardev@outlook.com)
- **Phone:** +201040946638
- **GitHub:** [https://github.com/ahmedomar2014/FTPChat](https://github.com/ahmedomar2014/FTPChat)
