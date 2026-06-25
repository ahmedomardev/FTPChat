# FTPChat

**Version: 2.2**  
**Type:** Custom Proprietary License  
**Author:** Ahmed Omar Saad  
**Contact:** <ahmedomardev@outlook.com>

---

## Highlights (v2.2)

- **Encrypted chat messages** (PBKDF2-SHA256 → Fernet) with **zlib compression** to reduce size.
- **FTP/FTPS/SFTP fallback**: the app attempts the most secure transport available and degrades gracefully when needed.
- **Threaded send/receive** and a timed **auto-refresh loop** to keep the UI responsive.
- **Offset/line-count based syncing** to minimize bandwidth usage.
- **Saved setups** (save/load/delete + per-setup notification ignore) and **modal setup** for faster configuration.
- **Tray minimization** support so the app can keep running in the background.
- **CustomTkinter GUI** with scrollable, non-editable chat history.
- Reworked/streamlined internals for a faster app.
- Added/expanded **saved setup management** (including ignore notifications).
- Added **tray minimization**.
- Added **modal setup form**.
- Added **SFTP → FTPS → FTP fallback** connection sequence.
- Improved message synchronization to reduce unnecessary downloads.

---

## New in v2.2

- Bug Fixes
