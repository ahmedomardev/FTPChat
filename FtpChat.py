"""
*Version: 1.7
FTPChat - Encrypted FTP-based Messaging Protocol  
Type: Custom Proprietary License
Author: Ahmed Omar Saad  
Contact: <ahmedomardev@outlook.com>

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the “Software”), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, and/or sublicense copies of  
the Software, subject to the following conditions: 

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
- **Commercial use of this software requires prior written permission from the author.**
- **The author reserves the right to relicense this software as closed-source or commercial at any time.**
- All rights to the name “FTPChat” and its protocol specification are retained by Ahmed Omar Saad.
  
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,  
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE  
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,  
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWAvRE.

Notes:
The author may offer separate commercial licenses for enterprise or closed-source use. Contact <ahmedomardev@outlook.com> for inquiries.
This license applies to all source code, documentation, and protocol specifications included in the FTPChat project.
"""

from random import uniform
from time import sleep
import customtkinter as ctk
from tkinter import messagebox
from base64 import urlsafe_b64encode
from datetime import datetime
from ftplib import FTP, FTP_TLS, all_errors
from io import BytesIO
from os import fdopen, remove
from tempfile import mkstemp
from threading import Thread
from webbrowser import open as open_link
from zlib import compress, decompress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# *--- GLOBALS ---
SALT = b"q6334#Q0q8294%E$(#$%^&^%$#@!#%^YHB>$W#CX>E"
CONNECTED = False
STORED_FTP_HOST = STORED_FTP_USER = STORED_FTP_PASS = STORED_CHAT_NAME = STORED_ENC_PASS = None
last_read_byte_offset = 0
refresh_after_id = None

# *--- Func. ---


def help_func():
    """
    Opens the official project documentation or support website.

    Uses the system's default web browser to navigate to the
    author's project portfolio.
    """
    open_link("ahmed-omar-software-projects.mydurable.com")


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Generates a secure cryptographic key from a plaintext password.

    Args:
        password (str): The user-provided encryption password.
        salt (bytes): A static salt used to defend against rainbow table attacks.

    Returns:
        bytes: A 32-byte raw key derived using PBKDF2HMAC with SHA256.
    """
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=100000)
    return kdf.derive(password.encode())


def encrypt_bytes(text: str) -> bytes:
    """
    Compresses and encrypts a string into a Fernet token.

    The process follows:
    1. UTF-8 Encoding -> 2. Zlib Compression -> 3. Fernet Encryption.

    Returns:
        bytes: The encrypted token ready for storage on the FTP server.
    """
    if STORED_ENC_PASS is None:
        return b""
    f = Fernet(urlsafe_b64encode(derive_key(STORED_ENC_PASS, SALT)))
    return f.encrypt(compress(text.encode("utf-8")))


def decrypt_bytes(data: bytes) -> str:
    """
    Decrypts and decompresses a byte-string back into readable text.

    Args:
        data (bytes): The encrypted line retrieved from the FTP file.

    Returns:
        str: The original plaintext message.
    """
    if STORED_ENC_PASS is None:
        return ""
    f = Fernet(urlsafe_b64encode(derive_key(STORED_ENC_PASS, SALT)))
    return decompress(f.decrypt(data)).decode("utf-8")


def ftp_connect(host, user, passwd):
    """
    Establishes a connection to the FTP server.

    Attempts an explicit FTPS (FTP over TLS) connection first for security.
    If FTPS fails, it falls back to a standard unsecured FTP connection.

    Returns:
        FTP_TLS | FTP: An active connection object.
    """
    try:
        ftp = FTP_TLS(host)
        ftp.login(user, passwd)
        ftp.prot_p()
        return ftp
    except:
        ftp = FTP(host)
        ftp.login(user, passwd)
        return ftp


def send_message_non(username, message):
    sleep(uniform(0.1, 0.8))
    """
    The background worker for uploading messages.

    Logic:
    1. Creates a local temporary file with the timestamped, encrypted message.
    2. Connects to FTP.
    3. Attempts to append (APPE) the data to the chat file.
    4. If APPE is not supported by the server, it performs a manual
       RETR (Download) -> Combine -> STOR (Upload) sequence.
    """
    try:
        ftp = ftp_connect(STORED_FTP_HOST, STORED_FTP_USER, STORED_FTP_PASS)
        tmp_fd, tmp_path = mkstemp()
        with fdopen(tmp_fd, "wb") as tmp_file:
            ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
            tmp_file.write(encrypt_bytes(
                f"{ts}:{username}: {message}".rstrip()) + b"\n")
        with open(tmp_path, "rb") as f:
            try:
                ftp.storbinary(f"APPE {STORED_CHAT_NAME}.txt", f)
            except:
                bio = BytesIO()
                try:
                    ftp.retrbinary(f"RETR {STORED_CHAT_NAME}.txt", bio.write)
                except:
                    pass
                f.seek(0)
                ftp.storbinary(f"STOR {STORED_CHAT_NAME}.txt", BytesIO(
                    bio.getvalue() + f.read()))
        remove(tmp_path)
        ftp.quit()
        main.after(0, lambda: message_widget.delete("1.0", "end"))
        read_messages()
    except all_errors as net_err:
        messagebox.showerror(
            "Protocol Error", f"FTP Transfer failed: {net_err}")
    except ConnectionError as conn_err:
        messagebox.showerror("Auth Error", str(conn_err))
    except Exception as e:
        messagebox.showerror("App Error", f"Logic failure: {e}")


def read_messages_non():
    """
    The background worker for fetching new messages.

    This function uses an offset-based approach (`last_read_byte_offset`)
    to fetch only new data added to the file since the last check,
    minimizing bandwidth usage.
    """
    global last_read_byte_offset
    if not CONNECTED:
        return
    try:
        ftp = ftp_connect(STORED_FTP_HOST, STORED_FTP_USER, STORED_FTP_PASS)
        file_path = f"{STORED_CHAT_NAME}.txt"
        current_size = ftp.size(file_path)
        if current_size > last_read_byte_offset:
            bio = BytesIO()
            ftp.retrbinary(f"RETR {file_path}", bio.write,
                           rest=last_read_byte_offset)
            lines = [decrypt_bytes(l)
                     for l in bio.getvalue().splitlines() if l.strip()]
            main.after(0, lambda: update_ui_text("\n".join(lines)))
            last_read_byte_offset = current_size
        ftp.quit()
    except:
        pass


def update_ui_text(txt):
    """Appends new content to the chat display in a thread-safe manner."""
    chat_display.configure(state="normal")
    chat_display.insert("end", txt + "\n")
    chat_display.see("end")
    chat_display.configure(state="disabled")


def auto_refresh():
    """
    Recursive UI timer that triggers a message check every 5 seconds.

    Only runs while the global 'CONNECTED' state is True.
    """
    global refresh_after_id
    if CONNECTED:
        read_messages_non()
        refresh_after_id = main.after(5000, auto_refresh)


def connect():
    """Establishes connection to the FTP server and starts auto-refresh."""
    global CONNECTED
    if not all([STORED_FTP_HOST, STORED_FTP_USER, STORED_FTP_PASS, STORED_CHAT_NAME, STORED_ENC_PASS]):
        messagebox.showwarning(
            "Warning", "Please use Setup for connection details")
        return
    try:
        ftp = ftp_connect(STORED_FTP_HOST, STORED_FTP_USER, STORED_FTP_PASS)
        CONNECTED = True
        status_label.configure(text="Connected", text_color="#4cc2ff")
        ftp.quit()
        auto_refresh()
    except Exception as e:
        messagebox.showerror("Fail", str(e))


def read_messages():
    """Threaded `read_messages_non` call to avoid UI blocking."""
    Thread(target=read_messages_non, daemon=True).start()


def send_messages(user, msg):
    """Threaded `send_message_non` call to avoid UI blocking."""
    if not CONNECTED:
        messagebox.showwarning("Warning", "Not connected to FTP server")
        return ""
    if not msg.strip():
        return
    Thread(target=send_message_non, args=(user, msg), daemon=True).start()


def alt_send_handler(event=None):
    send_button.configure(state="active")
    main.after(100, lambda: send_button.configure(state="normal"))
    send_messages(username_entry.get(), message_widget.get("1.0", "end-1c"))

# *--- UI SETUP ---


main = ctk.CTk()
main.title("FTPChat")
main.geometry("1920x1080")
main.state("zoomed")

# *Top Header Row
top_row = ctk.CTkFrame(main, fg_color="transparent")
top_row.pack(fill="x", padx=15, pady=15)

ctk.CTkLabel(top_row, text="Username:").pack(side="left")
username_entry = ctk.CTkEntry(top_row)
username_entry.pack(side="left", fill="x", expand=True, padx=10)

status_label = ctk.CTkLabel(top_row, text="Disconnected", text_color="gray")
status_label.pack(side="right", padx=10)


def open_setup_modal():
    """Opens the setup modal for entering FTP and encryption details."""
    modal = ctk.CTkToplevel(main)
    modal.title("Setup connection")
    modal.geometry("520x320")
    modal.transient(main)

    fields = [
        ("Host:", "STORED_FTP_HOST", None),
        ("FTP User:", "STORED_FTP_USER", None),
        ("Password:", "STORED_FTP_PASS", "*"),
        ("Chat File:", "STORED_CHAT_NAME", None),
        ("Encryption Key:", "STORED_ENC_PASS", "*"),
    ]
    entries = {}

    for label_text, attr, mask in fields:
        row = ctk.CTkFrame(modal)
        row.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(row, text=label_text, width=120).pack(side="left")
        ent = ctk.CTkEntry(row, show=mask)
        ent.pack(side="left", fill="x", expand=True)
        val = globals().get(attr)
        if val:
            ent.insert(0, val)
        entries[attr] = ent

    def on_ok():
        """Handles the OK button click in the setup modal."""
        global STORED_FTP_HOST, STORED_FTP_USER, STORED_FTP_PASS, STORED_CHAT_NAME, STORED_ENC_PASS
        (
            STORED_FTP_HOST,
            STORED_FTP_USER,
            STORED_FTP_PASS,
            STORED_CHAT_NAME,
            STORED_ENC_PASS,
        ) = [e.get().strip() for e in entries.values()]
        modal.destroy()
        connect()

    # *Buttons
    btn_row = ctk.CTkFrame(modal)
    btn_row.pack(pady=20, fill="x")
    ctk.CTkButton(btn_row, text="OK", command=on_ok).pack(
        side="left", expand=True, padx=10
    )
    ctk.CTkButton(
        btn_row, text="Cancel", command=modal.destroy
    ).pack(side="left", expand=True, padx=10)


ctk.CTkButton(top_row, text="Setup", command=open_setup_modal,
              width=100).pack(side="right")

# *Chat Display Area
ctk.CTkLabel(main, text="Chat:").pack(anchor="w", padx=15)
chat_display = ctk.CTkTextbox(
    main, corner_radius=5, border_width=1, height=300)
chat_display.pack(fill="both", padx=15, pady=5)
chat_display.configure(state="disabled")
chat_display.see("end")

# *Message Input Area
ctk.CTkLabel(main, text="Message:").pack(anchor="w", padx=15)
message_widget = ctk.CTkTextbox(
    main, height=300, corner_radius=5, border_width=1)
message_widget.pack(fill="x", padx=15, pady=5)
message_widget.see("end")

# *Send Button
send_button = ctk.CTkButton(main, text="Send", height=30, font=("Segoe UI", 13, "bold"),
                            command=lambda: send_messages(username_entry.get(), message_widget.get("1.0", "end-1c")))
send_button.pack(fill="x", padx=15, pady=15)
main.bind('<Alt_L>', alt_send_handler)
main.bind('<Alt_R>', alt_send_handler)
main.mainloop()
