from random import uniform
from time import sleep
from tkinter import messagebox
from base64 import urlsafe_b64encode
from datetime import datetime
from ftplib import FTP, FTP_TLS, all_errors
from io import BytesIO
from threading import Thread
from webbrowser import open as open_link
from zlib import compress, decompress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from paramiko import SSHClient, AutoAddPolicy
import customtkinter as ctk
import os
import json
import threading
import pystray
from PIL import Image, ImageDraw
from plyer import notification as _plyer_notification

main = None
chat_display = None
message_widget = None
send_button = None
status_label = None
username_entry = None
disconnect_button = None

# *--- GLOBALS ---
SALT = b"q6334#Q0q8294%E$(#$%^&^%$#@!#%^YHB>$W#CX>E"
CONNECTED = False
stored_ftp_host = stored_ftp_user = stored_ftp_pass = stored_chat_name = stored_enc_pass = stored_display_name = ""
stored_ignore_notifications = False
last_read_byte_offset = 0
last_line_count = 0
refresh_after_id = None
CURRENT_PROTOCOL = None


def init_app(
    _main,
    _chat_display,
    _message_widget,
    _send_button,
    _disconnect_button,
    _status_label,
    _username_entry,
    _saved_setups_container=None,
    _chat_title=None,
    _saved_setups_file=None,
):
    """
    Inject UI objects from FtpChat.py.

    This prevents circular imports: FtpChat imports functions, and functions must
    not import widgets from FtpChat at import-time.
    """
    global main, chat_display, message_widget, send_button, disconnect_button, status_label, username_entry
    main = _main
    chat_display = _chat_display
    message_widget = _message_widget
    send_button = _send_button
    disconnect_button = _disconnect_button
    status_label = _status_label
    username_entry = _username_entry
    # optional UI elements for saved setups
    global saved_setups_container, chat_title, saved_setups_file
    saved_setups_container = _saved_setups_container
    chat_title = _chat_title
    if _saved_setups_file:
        saved_setups_file = _saved_setups_file


def update_sidebar_connect_button(is_connected: bool):
    """Optional placeholder for sidebar connect button updates."""
    pass


# *--- Func. ---


def help_func():
    """
    Opens the official project documentation or support website.

    Uses the system's default web browser to navigate to the
    author's project portfolio.
    """
    open_link("https://ahmed-omar-software-projects.mydurable.com")


# --- Saved setups UI helpers (moved from main UI)
saved_setups = []
saved_setups_container = None
chat_title = None
saved_setups_file = os.path.join(
    os.path.dirname(__file__), "saved_setups.json")
tray_icon = None


def _create_tray_image():
    # Minimal generated image for tray icon
    if Image is None or ImageDraw is None:
        return None
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((8, 8, 56, 56), fill=(96, 165, 250, 255))
    return img


def minimize_to_tray():
    """Hide the main window and start a system tray icon to restore/quit."""
    global tray_icon
    if pystray is None:
        try:
            messagebox.showwarning(
                "Tray Unavailable", "pystray/Pillow not installed")
        except Exception:
            pass
        return
    try:
        main.withdraw()
    except Exception:
        pass

    def on_restore(icon, item):
        try:
            main.deiconify()
        except Exception:
            pass
        try:
            icon.stop()
        except Exception:
            pass

    def on_quit(icon, item):
        try:
            icon.stop()
        except Exception:
            pass
        try:
            main.destroy()
        except Exception:
            pass

    image = _create_tray_image()
    menu = (pystray.MenuItem('Restore', on_restore),
            pystray.MenuItem('Quit', on_quit))
    tray_icon = pystray.Icon('ftpchat', image, 'FTPChat', menu)

    def run_icon():
        try:
            tray_icon.run()
        except Exception:
            pass

    threading.Thread(target=run_icon, daemon=True).start()


def load_saved_setups():
    global saved_setups
    try:
        with open(saved_setups_file, "r", encoding="utf-8") as f:
            saved_setups = json.load(f)
    except FileNotFoundError:
        saved_setups = []
    except Exception:
        saved_setups = []


def persist_saved_setups():
    try:
        with open(saved_setups_file, "w", encoding="utf-8") as f:
            json.dump(saved_setups, f, indent=2)
    except Exception as e:
        try:
            messagebox.showerror("Save Error", f"Could not save setups:\n{e}")
        except Exception:
            pass


def save_setup_entry(name, display_name, host, user, passwd, chat_name, enc_pass):
    global saved_setups
    if not name.strip():
        try:
            messagebox.showwarning("Warning", "Save name cannot be empty.")
        except Exception:
            pass
        return
    existing = [item for item in saved_setups if item["name"] == name.strip()]
    new_entry = {
        "name": name.strip(),
        "display_name": display_name.strip(),
        "host": host,
        "user": user,
        "pass": passwd,
        "chat": chat_name,
        "enc": enc_pass,
        "ignore": globals().get("stored_ignore_notifications", False),
    }
    if existing:
        saved_setups = [
            item for item in saved_setups if item["name"] != name.strip()]
    saved_setups.append(new_entry)
    persist_saved_setups()
    try:
        render_saved_setups()
    except Exception:
        pass
    try:
        messagebox.showinfo("Saved", f"Setup '{name}' saved successfully.")
    except Exception:
        pass


def toggle_ignore(name):
    global saved_setups
    for item in saved_setups:
        if item.get("name") == name:
            item["ignore"] = not item.get("ignore", False)
            # If this is the selected setup, also update runtime flag
            try:
                if chat_title and chat_title.cget("text") == name:
                    globals()['stored_ignore_notifications'] = item["ignore"]
            except Exception:
                pass
            break
    persist_saved_setups()
    try:
        render_saved_setups()
    except Exception:
        pass


def delete_saved_setup(name):
    global saved_setups
    saved_setups = [item for item in saved_setups if item["name"] != name]
    persist_saved_setups()
    try:
        render_saved_setups()
    except Exception:
        pass


def load_saved_setup(setup):
    try:
        globals()['stored_ftp_host'] = setup["host"]
        globals()['stored_ftp_user'] = setup["user"]
        globals()['stored_ftp_pass'] = setup["pass"]
        globals()['stored_chat_name'] = setup["chat"]
        globals()['stored_enc_pass'] = setup["enc"]
        globals()['stored_ignore_notifications'] = setup.get("ignore", False)
        display_name = setup.get("display_name", setup["name"])
        globals()['stored_display_name'] = display_name
        if chat_title is not None:
            try:
                chat_title.configure(text=setup["name"])
            except Exception:
                pass
        if status_label is not None:
            try:
                status_label.configure(
                    text=f"Loaded {setup['name']}", text_color="#60a5fa")
            except Exception:
                pass
        try:
            render_saved_setups()
        except Exception:
            pass
    except Exception as e:
        try:
            messagebox.showerror("Load Error", f"Failed to load setup:\n{e}")
        except Exception:
            pass


def render_saved_setups():
    if saved_setups_container is None:
        return
    for child in saved_setups_container.winfo_children():
        child.destroy()
    for setup in saved_setups:
        is_selected = False
        try:
            is_selected = (chat_title.cget("text") == setup.get("name"))
        except Exception:
            is_selected = False
        row_frame = ctk.CTkFrame(
            saved_setups_container,
            fg_color="#0f1720" if not is_selected else "#07263b",
            corner_radius=18,
            border_width=1,
            border_color="#334155" if not is_selected else "#60a5fa",
        )
        row_frame.pack(fill="x", pady=6, padx=6)
        display_name = setup.get("display_name")
        button_text = setup["name"]
        if display_name:
            button_text += f" ({display_name})"
        ctk.CTkButton(
            row_frame,
            text=button_text,
            fg_color="#0f1720",
            hover_color="#1f2937",
            text_color="white",
            anchor="w",
            corner_radius=14,
            command=lambda item=setup: load_saved_setup(item),
        ).pack(side="left", fill="x", expand=True, padx=(10, 4), pady=10)
        ctk.CTkButton(
            row_frame,
            text="Delete",
            width=80,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda name=setup["name"]: delete_saved_setup(name),
        ).pack(side="right", padx=(4, 10), pady=10)
        ignore_state = setup.get("ignore", False)
        ignore_text = "Unignore" if ignore_state else "Ignore"
        ctk.CTkButton(
            row_frame,
            text=ignore_text,
            width=110,
            fg_color="#9ca3af" if not ignore_state else "#ef4444",
            hover_color="#6b7280",
            command=lambda name=setup["name"]: toggle_ignore(name),
        ).pack(side="right", padx=(4, 4), pady=10)


def open_setup_modal(save_only: bool = False):
    # Keep the modal implementation close to original but use globals
    modal = ctk.CTkToplevel(main)
    modal.title("Setup connection")
    modal.geometry("490x490")
    modal.resizable(False, False)
    modal.transient(main)
    modal.grab_set()
    modal.configure(fg_color="#0f1720")
    modal.grid_columnconfigure(1, weight=1)

    fields = [
        ("Save name:", "SETUP_NAME", None, "Home Chat"),
        ("Display Name:", "SETUP_DISPLAY_NAME", None, "Your name"),
        ("Host:", "STORED_FTP_HOST", None, "ftps.example.com"),
        ("FTP User:", "STORED_FTP_USER", None, "ftp_user"),
        ("Password:", "STORED_FTP_PASS", "*", None),
        ("Chat File:", "STORED_CHAT_NAME", None, "chatroom"),
        ("Encryption Key:", "STORED_ENC_PASS", "*", None),
    ]
    entries = {}
    default_values = {
        "STORED_FTP_HOST": stored_ftp_host,
        "STORED_FTP_USER": stored_ftp_user,
        "STORED_FTP_PASS": stored_ftp_pass,
        "STORED_CHAT_NAME": stored_chat_name,
        "STORED_ENC_PASS": stored_enc_pass,
        "SETUP_DISPLAY_NAME": stored_display_name or "",
        "STORED_IGNORE_NOTIFS": stored_ignore_notifications,
    }

    form_frame = ctk.CTkFrame(
        modal, fg_color="#111827", corner_radius=20, border_width=1, border_color="#1e293b")
    form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    form_frame.grid_columnconfigure(1, weight=1)

    for row_index, (label_text, attr, show_char, placeholder) in enumerate(fields):
        ctk.CTkLabel(form_frame, text=label_text, anchor="w", text_color="white").grid(
            row=row_index, column=0, padx=16, pady=10, sticky="w"
        )
        entry_kwargs = {"fg_color": "#0f1720",
                        "border_color": "#334155", "corner_radius": 14}
        if show_char is not None:
            entry_kwargs["show"] = show_char
        if placeholder is not None:
            entry_kwargs["placeholder_text"] = placeholder
        entry = ctk.CTkEntry(form_frame, **entry_kwargs)
        entry.grid(row=row_index, column=1, padx=(0, 16), pady=10, sticky="ew")
        if attr != "SETUP_NAME":
            value = default_values.get(attr)
            if value:
                entry.insert(0, value)
        entries[attr] = entry

    ignore_var = ctk.BooleanVar(
        value=default_values.get("STORED_IGNORE_NOTIFS", False))
    ctk.CTkLabel(form_frame, text="Ignore Notifications:", anchor="w", text_color="white").grid(
        row=len(fields), column=0, padx=16, pady=10, sticky="w"
    )
    ignore_cb = ctk.CTkCheckBox(
        form_frame, variable=ignore_var, text="Do not show notifications for this setup")
    ignore_cb.grid(row=len(fields), column=1,
                   padx=(0, 16), pady=10, sticky="w")

    def store_values():
        values = [e.get().strip() for e in entries.values()]
        if not all(values):
            try:
                messagebox.showwarning(
                    "Warning", "Please fill in all setup fields before continuing")
            except Exception:
                pass
            return None
        setup_name, display_name, host, user, passwd, chat_name, enc_pass = values
        globals()['stored_ftp_host'] = host
        globals()['stored_ftp_user'] = user
        globals()['stored_ftp_pass'] = passwd
        globals()['stored_chat_name'] = chat_name
        globals()['stored_enc_pass'] = enc_pass
        globals()['stored_display_name'] = display_name
        globals()['stored_ignore_notifications'] = bool(ignore_var.get())
        return setup_name, display_name

    def on_connect():
        result = store_values()
        if not result:
            return
        modal.destroy()
        try:
            connect()
            try:
                status_label.configure(text="Connected", text_color="green")
            except Exception:
                pass
            try:
                if disconnect_button is not None:
                    disconnect_button.configure(state="normal")
            except Exception:
                pass
            try:
                if 'update_sidebar_connect_button' in globals():
                    update_sidebar_connect_button(CURRENT_PROTOCOL is not None)
            except Exception:
                pass
        except Exception as e:
            try:
                messagebox.showerror("Connection Error",
                                     f"Failed to connect:\n{e}")
            except Exception:
                pass

    def on_save():
        result = store_values()
        if not result:
            return
        setup_name, display_name = result
        save_setup_entry(
            setup_name,
            display_name,
            stored_ftp_host,
            stored_ftp_user,
            stored_ftp_pass,
            stored_chat_name,
            stored_enc_pass,
        )

    buttons = ctk.CTkFrame(modal, fg_color="transparent")
    buttons.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")
    buttons.grid_columnconfigure(0, weight=1)
    buttons.grid_columnconfigure(1, weight=1)
    buttons.grid_columnconfigure(2, weight=1)

    ctk.CTkButton(buttons, text="Cancel", command=modal.destroy, fg_color="#475569").grid(
        row=0, column=0, sticky="ew", padx=(0, 10)
    )
    ctk.CTkButton(buttons, text="Save", command=on_save, fg_color="#38bdf8").grid(
        row=0, column=1, sticky="ew", padx=(0, 10)
    )
    if save_only:
        ctk.CTkButton(buttons, text="Done", command=modal.destroy, fg_color="#60a5fa").grid(
            row=0, column=2, sticky="ew"
        )
    else:
        ctk.CTkButton(buttons, text="Connect", command=on_connect, fg_color="#60a5fa").grid(
            row=0, column=2, sticky="ew"
        )


def notify(title: str, message: str):
    """Show a system notification (falls back to messagebox). Respects ignore flag."""
    global stored_ignore_notifications
    if stored_ignore_notifications:
        return
    try:
        if _plyer_notification is not None:
            _plyer_notification.notify(title=title, message=message, timeout=5)
            return
    except Exception:
        pass
    try:
        # Fallback: use tkinter messagebox on main thread
        if main is not None:
            main.after(0, lambda: messagebox.showinfo(title, message))
        else:
            messagebox.showinfo(title, message)
    except Exception:
        pass


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


def get_fernet() -> Fernet:
    """Creates a Fernet cipher from the configured encryption password."""
    if not stored_enc_pass:
        raise ValueError("Encryption key is required")
    return Fernet(urlsafe_b64encode(derive_key(stored_enc_pass, SALT)))


def normalize_chat_filename(chat_name: str) -> str:
    """Ensure the chat file has a normalized filename ending in .txt."""
    if not chat_name:
        chat_name = "chat"
    file_name = chat_name.strip()
    if not file_name.lower().endswith(".txt"):
        file_name += ".txt"
    return file_name


def encrypt_bytes(text: str) -> bytes:
    """
    Compresses and encrypts a string into a Fernet token.

    The process follows:
    1. UTF-8 Encoding -> 2. Zlib Compression -> 3. Fernet Encryption.

    Returns:
        bytes: The encrypted token ready for storage on the FTP server.
    """
    f = get_fernet()
    return f.encrypt(compress(text.encode("utf-8")))


def decrypt_bytes(data: bytes) -> str:
    """
    Decrypts and decompresses a byte-string back into readable text.

    Args:
        data (bytes): The encrypted line retrieved from the FTP file.

    Returns:
        str: The original plaintext message.
    """
    f = get_fernet()
    return decompress(f.decrypt(data)).decode("utf-8")


def ftp_connect(host, user, passwd):
    """
    Establishes a connection to the server.

    Attempts SFTP first for security, then FTPS, then FTP.

    Returns:
        tuple: (connection, ssh_client) where connection is SFTPClient or FTP, ssh_client is SSHClient or None.
    """
    last_error = None
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=user, password=passwd, timeout=10)
        sftp = ssh.open_sftp()
        return sftp, ssh
    except Exception as exc:
        last_error = exc
    try:
        ftp = FTP_TLS(host, timeout=10)
        ftp.login(user, passwd)
        ftp.prot_p()
        return ftp, None
    except Exception as exc:
        last_error = exc
    try:
        ftp = FTP(host, timeout=10)
        ftp.login(user, passwd)
        return ftp, None
    except Exception as exc:
        last_error = exc
    raise ConnectionError(f"Unable to connect via SFTP/FTPS/FTP: {last_error}")


def send_message_non(username, message):
    sleep(uniform(0.1, 0.8))
    """
    The background worker for uploading messages.

    For FTP: Attempts to append (APPE) the data to the chat file.
    If APPE is not supported, it performs a manual RETR (Download) -> Combine -> STOR (Upload) sequence.
    For SFTP: Downloads whole file, appends new data, uploads whole file.
    """
    try:
        conn, ssh = ftp_connect(
            stored_ftp_host, stored_ftp_user, stored_ftp_pass)
        file_path = normalize_chat_filename(stored_chat_name)
        ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        new_data = encrypt_bytes(
            f"{ts}:{username}: {message}".rstrip()) + b"\n"
        if ssh:  # SFTP
            existing_data = b""
            try:
                with conn.open(file_path, "rb") as remote_file:
                    existing_data = remote_file.read()
            except Exception:
                existing_data = b""
            with conn.open(file_path, "wb") as remote_file:
                remote_file.write(existing_data + new_data)
            conn.close()
            ssh.close()
        else:  # FTP / FTPS data connection
            try:
                conn.storbinary(f"APPE {file_path}", BytesIO(new_data))
            except Exception as e:
                err = str(e).lower()
                # Some vsftpd servers require SSL session reuse (522). If so,
                # retry the upload over a plain FTP connection as a pragmatic
                # fallback (server-side fix preferred).
                if isinstance(conn, FTP_TLS) and ("session reuse" in err or "522" in err):
                    try:
                        plain = FTP(stored_ftp_host, timeout=10)
                        plain.login(stored_ftp_user, stored_ftp_pass)
                        plain.storbinary(
                            f"APPE {file_path}", BytesIO(new_data))
                        plain.quit()
                        conn.quit()
                        main.after(
                            0, lambda: message_widget.delete("1.0", "end"))
                        read_messages()
                        try:
                            notify(
                                f"Message sent ({username})", (message or "").strip()[:200])
                        except Exception:
                            pass
                        return
                    except Exception:
                        # fall through to the combine/upload attempt below
                        pass

                existing_data = BytesIO()
                try:
                    conn.retrbinary(f"RETR {file_path}", existing_data.write)
                except all_errors:
                    existing_data = BytesIO()
                combined = existing_data.getvalue() + new_data
                try:
                    conn.storbinary(f"STOR {file_path}", BytesIO(combined))
                except Exception as e2:
                    err2 = str(e2).lower()
                    if isinstance(conn, FTP_TLS) and ("session reuse" in err2 or "522" in err2):
                        # Try plain FTP for the final upload
                        plain = FTP(stored_ftp_host, timeout=10)
                        try:
                            plain.login(stored_ftp_user, stored_ftp_pass)
                            plain.storbinary(
                                f"STOR {file_path}", BytesIO(combined))
                            plain.quit()
                        except Exception:
                            plain.quit()
                            raise
                    else:
                        raise
            try:
                conn.quit()
            except Exception:
                pass
        main.after(0, lambda: message_widget.delete("1.0", "end"))
        read_messages()
        try:
            notify(f"Message sent ({username})", (message or "").strip()[:200])
        except Exception:
            pass
    except all_errors as net_err:
        messagebox.showerror(
            "Protocol Error", f"Transfer failed: {net_err}")
    except ConnectionError as conn_err:
        messagebox.showerror("Connection Error", str(conn_err))
    except Exception as e:
        messagebox.showerror("Application Error",
                             f"Failed to send message: {e}")
    finally:
        if send_button is not None:
            main.after(0, lambda: send_button.configure(state="normal"))


def read_messages_non():
    """
    The background worker for fetching new messages.

    For FTP: Uses offset-based approach to fetch only new data.
    For SFTP: Downloads whole file, uses line count to append only new lines.
    """
    global last_read_byte_offset, last_line_count
    if not CONNECTED:
        return
    try:
        conn, ssh = ftp_connect(
            stored_ftp_host, stored_ftp_user, stored_ftp_pass)
        file_path = normalize_chat_filename(stored_chat_name)
        if ssh:  # SFTP
            data = b""
            try:
                with conn.open(file_path, "rb") as remote_file:
                    data = remote_file.read()
            except Exception:
                data = b""
            if data:
                lines = [decrypt_bytes(l)
                         for l in data.splitlines() if l.strip()]
                if len(lines) > last_line_count:
                    new_lines = lines[last_line_count:]
                    main.after(0, lambda: update_ui_text("\n".join(new_lines)))
                    last_line_count = len(lines)
                    try:
                        notify("New messages", "\n".join(new_lines[-3:]))
                    except Exception:
                        pass
            conn.close()
            ssh.close()
        else:  # FTP
            try:
                current_size = conn.size(file_path)
            except all_errors:
                conn.quit()
                return
            if current_size < last_read_byte_offset:
                last_read_byte_offset = 0
            if current_size > last_read_byte_offset:
                bio = BytesIO()
                try:
                    conn.retrbinary(f"RETR {file_path}", bio.write,
                                    rest=last_read_byte_offset)
                except Exception as e:
                    err = str(e).lower()
                    # Retry over plain FTP if FTPS rejects with session-reuse error
                    if isinstance(conn, FTP_TLS) and ("session reuse" in err or "522" in err):
                        try:
                            plain = FTP(stored_ftp_host, timeout=10)
                            plain.login(stored_ftp_user, stored_ftp_pass)
                            bio = BytesIO()
                            plain.retrbinary(f"RETR {file_path}", bio.write,
                                             rest=last_read_byte_offset)
                            plain.quit()
                        except Exception:
                            bio = BytesIO()
                    else:
                        bio = BytesIO()

                lines = [decrypt_bytes(l)
                         for l in bio.getvalue().splitlines() if l.strip()]
                if lines:
                    main.after(0, lambda: update_ui_text("\n".join(lines)))
                    try:
                        notify("New messages", "\n".join(lines[-3:]))
                    except Exception:
                        pass
                last_read_byte_offset = current_size
            conn.quit()
    except Exception:
        pass


def update_ui_text(txt):
    """Appends new content to the chat display in a thread-safe manner."""
    if not txt:
        return
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
        read_messages()
        refresh_after_id = main.after(5000, auto_refresh)


def connect():
    """Establishes connection to the server and starts auto-refresh."""
    global CONNECTED, CURRENT_PROTOCOL
    if not all([stored_ftp_host, stored_ftp_user, stored_ftp_pass, stored_chat_name, stored_enc_pass]):
        messagebox.showwarning(
            "Warning", "Please use Setup for connection details")
        return
    try:
        status_label.configure(text="Connecting...", text_color="#fbbf24")
        conn, ssh = ftp_connect(
            stored_ftp_host, stored_ftp_user, stored_ftp_pass)
        CONNECTED = True
        if ssh:
            CURRENT_PROTOCOL = "SFTP"
        elif isinstance(conn, FTP_TLS):
            CURRENT_PROTOCOL = "FTPS"
        else:
            CURRENT_PROTOCOL = "FTP"
        status_label.configure(
            text=f"Connected ({CURRENT_PROTOCOL})", text_color="#4cc2ff")
        if disconnect_button is not None:
            disconnect_button.configure(state="normal")
        if ssh:  # SFTP
            conn.close()
            ssh.close()
        else:  # FTP
            conn.quit()
        read_messages()
        auto_refresh()
    except Exception as e:
        CONNECTED = False
        CURRENT_PROTOCOL = None
        status_label.configure(text="Disconnected", text_color="gray")
        if disconnect_button is not None:
            disconnect_button.configure(state="normal")
        messagebox.showerror("Connection Failed", str(e))


def disconnect():
    """Stops refresh and updates the UI when the user disconnects."""
    global CONNECTED, CURRENT_PROTOCOL, refresh_after_id
    CONNECTED = False
    CURRENT_PROTOCOL = None
    if refresh_after_id is not None:
        try:
            main.after_cancel(refresh_after_id)
        except Exception:
            pass
        refresh_after_id = None
    status_label.configure(text="Disconnected", text_color="gray")
    if disconnect_button is not None:
        disconnect_button.configure(state="normal")
    update_ui_text(">>> Disconnected from server")


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
    if send_button is not None:
        send_button.configure(state="disabled")
    Thread(target=send_message_non, args=(user, msg), daemon=True).start()


def return_send_handler(event=None):
    display_name = stored_display_name or "Anonymous"
    send_messages(display_name, message_widget.get("1.0", "end-1c"))
    return "break"
