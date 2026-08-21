"""
Version: 2.3
FTPChat - Encrypted FTP-based Messaging Protocol
Type: Custom Proprietary License
Author: Ahmed Omar Saad
Contact: <ahmedomardev@outlook.com>
"""

import os
import sys
import json
from random import uniform
from time import sleep
from base64 import urlsafe_b64encode
from datetime import datetime
from ftplib import FTP
from io import BytesIO
from threading import Thread, Lock
from webbrowser import open as open_link
from zlib import compress, decompress

import flet as ft
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from paramiko import SSHClient, AutoAddPolicy

# *--- MINIMALIST THEME COLORS ---
BG_MAIN = "#090d16"
BG_SURFACE = "#111827"
BG_INPUT = "#030712"
BORDER_COLOR = "#1f2937"
ACCENT_BLUE = "#3b82f6"
TEXT_MUTED = "#9ca3af"

# *--- GLOBALS ---
SALT = b"q6334#Q0q8294%E$(#$%^&^%$#@!#%^YHB>$W#CX>E"
CONNECTED = False
stored_ftp_host = stored_ftp_user = stored_ftp_pass = stored_chat_name = (
    stored_enc_pass
) = stored_display_name = ""
last_read_byte_offset = 0
last_line_count = 0
CURRENT_PROTOCOL = None

net_lock = Lock()
saved_setups = []

if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

saved_setups_file = os.path.join(base_dir, "saved_setups.json")

# *--- CRYPTO & UTILS ---


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return kdf.derive(password.encode())


def encrypt_bytes(text: str) -> bytes:
    if not stored_enc_pass:
        return b""
    f = Fernet(urlsafe_b64encode(derive_key(stored_enc_pass, SALT)))
    return f.encrypt(compress(text.encode("utf-8")))


def decrypt_bytes(data: bytes) -> str:
    if not stored_enc_pass:
        return ""
    try:
        f = Fernet(urlsafe_b64encode(derive_key(stored_enc_pass, SALT)))
        return decompress(f.decrypt(data)).decode("utf-8")
    except Exception:
        try:
            decoded = data.decode("utf-8", errors="ignore").strip()
            if decoded:
                return f"[Plaintext/Wrong Password]: {decoded}"
        except Exception:
            pass
        return "[Decryption Error - Corrupted Data]"


def ftp_connect(host, user, passwd):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=user, password=passwd, timeout=10)
        sftp = ssh.open_sftp()
        return sftp, ssh
    except Exception:
        pass
    try:
        ftp = FTP(host, timeout=10)
        ftp.login(user, passwd)
        return ftp, None
    except Exception:
        return None, None


def load_saved_setups():
    global saved_setups
    try:
        with open(saved_setups_file, "r", encoding="utf-8") as f:
            saved_setups = json.load(f)
    except Exception:
        saved_setups = []


def persist_saved_setups():
    try:
        with open(saved_setups_file, "w", encoding="utf-8") as f:
            json.dump(saved_setups, f, indent=2)
    except Exception:
        pass


def create_border(color=BORDER_COLOR, width=1):
    return ft.Border.all(width, color)


# *--- MAIN APP ---


def main(page: ft.Page):
    page.title = "FTPChat"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_MAIN
    page.padding = 16
    page.spacing = 12

    load_saved_setups()

    def safe_open(control):
        if hasattr(page, "open"):
            page.open(control)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(control)
        else:
            if isinstance(control, ft.SnackBar):
                page.snack_bar = control
                control.open = True
            else:
                page.dialog = control
                control.open = True
            page.update()

    def safe_close(control):
        if hasattr(page, "close"):
            page.close(control)
        else:
            control.open = False
            page.update()

    def show_snackbar(msg: str):
        safe_open(ft.SnackBar(content=ft.Text(msg, size=13)))

    # Header Controls
    status_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=TEXT_MUTED)
    status_text = ft.Text(
        "Offline", color=TEXT_MUTED, size=12, weight=ft.FontWeight.W_500
    )

    status_indicator = ft.Row(
        [status_dot, status_text], spacing=6, alignment=ft.MainAxisAlignment.START
    )

    chat_display = ft.ListView(expand=True, spacing=6, auto_scroll=True)

    message_input = ft.TextField(
        hint_text="Type a message...",
        multiline=True,
        min_lines=1,
        max_lines=3,
        bgcolor=BG_INPUT,
        border_color=BORDER_COLOR,
        border_radius=8,
        content_padding=12,
        text_size=13,
        expand=True,
    )

    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=ACCENT_BLUE,
        icon_size=20,
        tooltip="Send",
    )

    disconnect_btn = ft.TextButton(
        "Disconnect",
        style=ft.ButtonStyle(color="#ef4444"),
        visible=False,
    )

    def append_chat_line(txt: str):
        if not txt:
            return
        chat_display.controls.append(
            ft.Text(txt, size=13, color="#e5e7eb", font_family="monospace")
        )
        page.update()

    # Network Logic
    def send_message_non(display_name, message):
        sleep(uniform(0.1, 0.3))
        try:
            with net_lock:
                conn, ssh = ftp_connect(
                    stored_ftp_host, stored_ftp_user, stored_ftp_pass
                )
                if not conn:
                    raise ConnectionError("Server unavailable")

                file_path = (
                    f"{stored_chat_name}.txt"
                    if not stored_chat_name.endswith(".txt")
                    else stored_chat_name
                )
                ts = datetime.now().astimezone().strftime("%H:%M")
                new_data = (
                    encrypt_bytes(f"[{ts}] {display_name}: {message}".rstrip()) + b"\n"
                )

                if ssh:
                    existing_data = b""
                    try:
                        with conn.open(file_path, "rb") as rf:
                            existing_data = rf.read()
                    except Exception:
                        pass
                    with conn.open(file_path, "wb") as rf:
                        rf.write(existing_data + new_data)
                    conn.close()
                    ssh.close()
                else:
                    try:
                        conn.storbinary(f"APPE {file_path}", BytesIO(new_data))
                    except Exception:
                        bio = BytesIO()
                        try:
                            conn.retrbinary(f"RETR {file_path}", bio.write)
                        except Exception:
                            pass
                        combined = bio.getvalue() + new_data
                        conn.storbinary(f"STOR {file_path}", BytesIO(combined))
                    conn.quit()

            message_input.value = ""
            read_messages_thread()
        except Exception as err:
            show_snackbar(f"Failed to send: {err}")
        finally:
            send_btn.disabled = False
            page.update()

    def read_messages_non():
        global last_read_byte_offset, last_line_count
        if not CONNECTED or not net_lock.acquire(blocking=False):
            return

        try:
            conn, ssh = ftp_connect(stored_ftp_host, stored_ftp_user, stored_ftp_pass)
            if not conn:
                return
            file_path = (
                f"{stored_chat_name}.txt"
                if not stored_chat_name.endswith(".txt")
                else stored_chat_name
            )
            my_user = stored_display_name or "User"

            if ssh:
                data = b""
                try:
                    with conn.open(file_path, "rb") as rf:
                        data = rf.read()
                except Exception:
                    pass
                if data:
                    raw_lines = [
                        decrypt_bytes(l) for l in data.splitlines() if l.strip()
                    ]
                    lines = [
                        (
                            l.replace(f" {my_user}:", " You:", 1)
                            if f" {my_user}:" in l
                            else l
                        )
                        for l in raw_lines
                    ]
                    if len(lines) > last_line_count:
                        for line in lines[last_line_count:]:
                            append_chat_line(line)
                        last_line_count = len(lines)
                conn.close()
                ssh.close()
            else:
                try:
                    current_size = conn.size(file_path)
                except Exception:
                    conn.quit()
                    return
                if current_size < last_read_byte_offset:
                    last_read_byte_offset = 0
                    last_line_count = 0

                if current_size > last_read_byte_offset:
                    bio = BytesIO()
                    conn.retrbinary(
                        f"RETR {file_path}", bio.write, rest=last_read_byte_offset
                    )
                    raw_lines = [
                        decrypt_bytes(l)
                        for l in bio.getvalue().splitlines()
                        if l.strip()
                    ]
                    lines = [
                        (
                            l.replace(f" {my_user}:", " You:", 1)
                            if f" {my_user}:" in l
                            else l
                        )
                        for l in raw_lines
                    ]
                    for line in lines:
                        append_chat_line(line)
                    last_read_byte_offset = current_size
                conn.quit()
        except Exception:
            pass
        finally:
            net_lock.release()

    def read_messages_thread():
        Thread(target=read_messages_non, daemon=True).start()

    def on_send(e):
        if not CONNECTED:
            show_snackbar("Connect to a server first")
            return
        msg = message_input.value.strip()
        if not msg:
            return
        send_btn.disabled = True
        page.update()
        user = stored_display_name or "User"
        Thread(target=send_message_non, args=(user, msg), daemon=True).start()

    send_btn.on_click = on_send

    def auto_refresh():
        while True:
            if CONNECTED:
                read_messages_non()
            sleep(4)

    Thread(target=auto_refresh, daemon=True).start()

    def connect():
        global CONNECTED, CURRENT_PROTOCOL, last_read_byte_offset, last_line_count
        if not all(
            [
                stored_ftp_host,
                stored_ftp_user,
                stored_ftp_pass,
                stored_chat_name,
                stored_enc_pass,
            ]
        ):
            show_snackbar("Profile incomplete")
            return
        try:
            status_dot.bgcolor = "#f59e0b"
            status_text.value = "Connecting"
            page.update()

            conn, ssh = ftp_connect(stored_ftp_host, stored_ftp_user, stored_ftp_pass)
            if not conn:
                raise ConnectionError("Authentication failed")

            last_read_byte_offset = 0
            last_line_count = 0
            CONNECTED = True
            CURRENT_PROTOCOL = "SFTP" if ssh else "FTP"

            status_dot.bgcolor = "#22c55e"
            status_text.value = (
                f"{CURRENT_PROTOCOL} ({stored_display_name or 'Connected'})"
            )
            disconnect_btn.visible = True

            if ssh:
                conn.close()
                ssh.close()
            else:
                conn.quit()

            page.update()
            read_messages_thread()
        except Exception as err:
            CONNECTED = False
            status_dot.bgcolor = TEXT_MUTED
            status_text.value = "Offline"
            disconnect_btn.visible = False
            show_snackbar(f"Connection failed: {err}")
            page.update()

    def disconnect(e=None):
        global CONNECTED, CURRENT_PROTOCOL
        CONNECTED = False
        CURRENT_PROTOCOL = None
        disconnect_btn.visible = False
        status_dot.bgcolor = TEXT_MUTED
        status_text.value = "Offline"
        append_chat_line("— Disconnected —")
        page.update()

    disconnect_btn.on_click = disconnect

    # Minimal Modals
    def open_setup_modal(e=None):
        name_in = ft.TextField(label="Profile Name", border_color=BORDER_COLOR)
        display_name_in = ft.TextField(
            label="Display Name", value=stored_display_name, border_color=BORDER_COLOR
        )
        host_in = ft.TextField(
            label="Host / IP", value=stored_ftp_host, border_color=BORDER_COLOR
        )
        user_in = ft.TextField(
            label="User", value=stored_ftp_user, border_color=BORDER_COLOR
        )
        pass_in = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            value=stored_ftp_pass,
            border_color=BORDER_COLOR,
        )
        chat_in = ft.TextField(
            label="Room (.txt)", value=stored_chat_name, border_color=BORDER_COLOR
        )
        enc_in = ft.TextField(
            label="Encryption Key",
            password=True,
            can_reveal_password=True,
            value=stored_enc_pass,
            border_color=BORDER_COLOR,
        )

        def save(e):
            global stored_ftp_host, stored_ftp_user, stored_ftp_pass, stored_chat_name, stored_enc_pass, stored_display_name, saved_setups
            if not all(
                [
                    name_in.value,
                    display_name_in.value,
                    host_in.value,
                    user_in.value,
                    pass_in.value,
                    chat_in.value,
                    enc_in.value,
                ]
            ):
                show_snackbar("Please fill in all fields")
                return

            stored_ftp_host = host_in.value.strip()
            stored_ftp_user = user_in.value.strip()
            stored_ftp_pass = pass_in.value.strip()
            stored_chat_name = chat_in.value.strip()
            stored_enc_pass = enc_in.value.strip()
            stored_display_name = display_name_in.value.strip() or "User"

            profile = {
                "name": name_in.value.strip(),
                "display_name": stored_display_name,
                "host": stored_ftp_host,
                "user": stored_ftp_user,
                "pass": stored_ftp_pass,
                "chat": stored_chat_name,
                "enc": stored_enc_pass,
            }
            saved_setups = [i for i in saved_setups if i["name"] != profile["name"]]
            saved_setups.append(profile)
            persist_saved_setups()

            safe_close(modal)
            connect()

        modal = ft.AlertDialog(
            title=ft.Text("Server Setup", size=16, weight=ft.FontWeight.W_600),
            content=ft.Column(
                [name_in, display_name_in, host_in, user_in, pass_in, chat_in, enc_in],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: safe_close(modal)),
                ft.TextButton(
                    "Save & Connect",
                    style=ft.ButtonStyle(color=ACCENT_BLUE),
                    on_click=save,
                ),
            ],
        )
        safe_open(modal)

    def open_saves_modal(e=None):
        saves_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

        def load_profile(s):
            global stored_ftp_host, stored_ftp_user, stored_ftp_pass, stored_chat_name, stored_enc_pass, stored_display_name
            stored_ftp_host, stored_ftp_user, stored_ftp_pass = (
                s["host"],
                s["user"],
                s["pass"],
            )
            stored_chat_name, stored_enc_pass = s["chat"], s["enc"]
            stored_display_name = s.get("display_name", s["name"])
            safe_close(modal)
            connect()

        def remove_profile(name):
            global saved_setups
            saved_setups = [i for i in saved_setups if i["name"] != name]
            persist_saved_setups()
            render()

        def render():
            saves_col.controls.clear()
            if not saved_setups:
                saves_col.controls.append(
                    ft.Text("No saved servers.", color=TEXT_MUTED, size=13)
                )
            else:
                for s in saved_setups:
                    saves_col.controls.append(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(
                                        f"{s['name']} ({s.get('display_name', 'User')})",
                                        size=13,
                                        weight=ft.FontWeight.W_500,
                                        expand=True,
                                    ),
                                    ft.IconButton(
                                        ft.Icons.PLAY_ARROW_ROUNDED,
                                        icon_size=18,
                                        icon_color=ACCENT_BLUE,
                                        on_click=lambda e, setup=s: load_profile(setup),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.CLOSE_ROUNDED,
                                        icon_size=18,
                                        icon_color="#ef4444",
                                        on_click=lambda e, n=s["name"]: remove_profile(
                                            n
                                        ),
                                    ),
                                ]
                            ),
                            bgcolor=BG_INPUT,
                            border=create_border(),
                            border_radius=6,
                            padding=8,
                        )
                    )
            page.update()

        modal = ft.AlertDialog(
            title=ft.Text("Saved Servers", size=16, weight=ft.FontWeight.W_600),
            content=ft.Container(saves_col, width=320, height=220),
            actions=[ft.TextButton("Close", on_click=lambda e: safe_close(modal))],
        )
        render()
        safe_open(modal)

    header = ft.Container(
        content=ft.Row(
            [
                status_indicator,
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.STORAGE_ROUNDED,
                            icon_size=18,
                            icon_color=TEXT_MUTED,
                            tooltip="Saved Servers",
                            on_click=open_saves_modal,
                        ),
                        ft.IconButton(
                            ft.Icons.ADD_ROUNDED,
                            icon_size=18,
                            icon_color=ACCENT_BLUE,
                            tooltip="New Server",
                            on_click=open_setup_modal,
                        ),
                        disconnect_btn,
                    ],
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=BG_SURFACE,
        border=create_border(),
        border_radius=8,
        padding=ft.Padding(12, 6, 12, 6),
    )

    chat_box = ft.Container(
        content=chat_display,
        bgcolor=BG_SURFACE,
        border=create_border(),
        border_radius=8,
        padding=12,
        expand=True,
    )

    input_box = ft.Row([message_input, send_btn], spacing=6)

    page.add(header, chat_box, input_box)


if __name__ == "__main__":
    ft.app(target=main)
    ft.app(target=main, assets_dir="assets")
