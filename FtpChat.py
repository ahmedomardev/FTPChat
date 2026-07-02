"""
Version: 2.2
FTPChat - Encrypted FTP-based Messaging Protocol
Type: Custom Proprietary License
Author: Ahmed Omar Saad
Contact: <ahmedomardev@outlook.com>
"""

import time
from random import uniform
from time import sleep
import customtkinter as ctk
from tkinter import messagebox
from base64 import urlsafe_b64encode
from datetime import datetime
from ftplib import FTP
from io import BytesIO
import os
import sys
import json
from threading import Thread, Lock
from webbrowser import open as open_link
from zlib import compress, decompress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from paramiko import SSHClient, AutoAddPolicy
import requests

BG_MAIN = "#0b0f19"
BG_CARD = "#0e1626"
BG_INPUT = "#070b12"
COLOR_BLUE = "#539bf5"
COLOR_GREEN = "#22c55e"
COLOR_BORDER = "#1b273a"

ctk.set_appearance_mode("dark")

# *--- GLOBALS ---
SALT = b"q6334#Q0q8294%E$(#$%^&^%$#@!#%^YHB>$W#CX>E"
CONNECTED = False
stored_ftp_host = stored_ftp_user = stored_ftp_pass = stored_chat_name = (
    stored_enc_pass
) = stored_display_name = ""
last_read_byte_offset = 0
last_line_count = 0
refresh_after_id = None
CURRENT_PROTOCOL = None

net_lock = Lock()

saved_setups = []

# Determine the absolute path safely, even if compiled to an .exe
if getattr(sys, "frozen", False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Both configurations now use the absolute safe directory
saved_setups_file = os.path.join(base_dir, "saved_setups.json")

# *--- Func. ---


def help_func():
    open_link("https://ahmed-omar-software-projects.mydurable.com")


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


def send_message_non(username, message):
    sleep(uniform(0.1, 0.4))
    try:
        with net_lock:
            conn, ssh = ftp_connect(stored_ftp_host, stored_ftp_user, stored_ftp_pass)
            if not conn:
                raise ConnectionError("Could not reach the server.")

            file_path = (
                f"{stored_chat_name}.txt"
                if not stored_chat_name.endswith(".txt")
                else stored_chat_name
            )
            ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
            new_data = encrypt_bytes(f"{ts}:{username}: {message}".rstrip()) + b"\n"

            if ssh:
                existing_data = b""
                try:
                    with conn.open(file_path, "rb") as remote_file:
                        existing_data = remote_file.read()
                except Exception:
                    pass
                with conn.open(file_path, "wb") as remote_file:
                    remote_file.write(existing_data + new_data)
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

        main.after(0, lambda: message_widget.delete("1.0", "end"))
        read_messages()
    except Exception as e:
        main.after(
            0,
            lambda: messagebox.showerror("Transmission Error", f"Failed to send: {e}"),
        )
    finally:
        main.after(0, lambda: send_button.configure(state="normal"))


def read_messages_non():
    global last_read_byte_offset, last_line_count
    if not CONNECTED:
        return

    if not net_lock.acquire(blocking=False):
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
        my_username = stored_display_name or "Anonymous"

        if ssh:
            data = b""
            try:
                with conn.open(file_path, "rb") as remote_file:
                    data = remote_file.read()
            except Exception:
                pass
            if data:
                raw_lines = [decrypt_bytes(l) for l in data.splitlines() if l.strip()]
                lines = [
                    (
                        l.replace(f":{my_username}:", ":[YOU]:", 1)
                        if f":{my_username}:" in l
                        else l
                    )
                    for l in raw_lines
                ]
                if len(lines) > last_line_count:
                    new_lines = lines[last_line_count:]
                    main.after(0, lambda nl=new_lines: update_ui_text("\n".join(nl)))
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
                    decrypt_bytes(l) for l in bio.getvalue().splitlines() if l.strip()
                ]
                lines = [
                    (
                        l.replace(f":{my_username}:", ":[YOU]:", 1)
                        if f":{my_username}:" in l
                        else l
                    )
                    for l in raw_lines
                ]
                if lines:
                    main.after(0, lambda lns=lines: update_ui_text("\n".join(lns)))
                last_read_byte_offset = current_size
            conn.quit()
    except Exception:
        pass
    finally:
        net_lock.release()


def update_ui_text(txt):
    if not txt:
        return
    chat_display.configure(state="normal")
    chat_display.insert("end", txt + "\n")
    chat_display.see("end")
    chat_display.configure(state="disabled")


def auto_refresh():
    global refresh_after_id
    if CONNECTED:
        read_messages()
        refresh_after_id = main.after(5000, auto_refresh)


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
        messagebox.showwarning("Warning", "Please configure profile details first.")
        return
    try:
        status_label.configure(text="Connecting...", text_color="#fbbf24")
        conn, ssh = ftp_connect(stored_ftp_host, stored_ftp_user, stored_ftp_pass)
        if not conn:
            raise ConnectionError("Server could not be verified.")

        last_read_byte_offset = 0
        last_line_count = 0

        CONNECTED = True
        CURRENT_PROTOCOL = "SFTP" if ssh else "FTP"
        status_label.configure(
            text=f"Connected ({CURRENT_PROTOCOL})", text_color=COLOR_BLUE
        )

        disconnect_button.pack(side="right", padx=5)

        if ssh:
            conn.close()
            ssh.close()
        else:
            conn.quit()
        read_messages()
        auto_refresh()
    except Exception as e:
        CONNECTED = False
        CURRENT_PROTOCOL = None
        status_label.configure(text="Disconnected", text_color="gray")
        disconnect_button.pack_forget()
        messagebox.showerror("Connection Failed", str(e))


def disconnect_handler():
    global CONNECTED, CURRENT_PROTOCOL, refresh_after_id
    CONNECTED = False
    CURRENT_PROTOCOL = None
    if refresh_after_id:
        try:
            main.after_cancel(refresh_after_id)
        except Exception:
            pass
        refresh_after_id = None

    disconnect_button.pack_forget()
    status_label.configure(text="Disconnected", text_color="gray")
    update_ui_text(">>> Disconnected from the server.")


def read_messages():
    Thread(target=read_messages_non, daemon=True).start()


def send_messages(user, msg):
    if not CONNECTED:
        messagebox.showwarning("Warning", "Not connected to server")
        return
    if not msg.strip():
        return
    send_button.configure(state="disabled")
    Thread(target=send_message_non, args=(user, msg), daemon=True).start()


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
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not write configuration:\n{e}")


def direct_connect_profile(setup, modal_context):
    global stored_ftp_host, stored_ftp_user, stored_ftp_pass, stored_chat_name, stored_enc_pass, stored_display_name
    stored_ftp_host = setup["host"]
    stored_ftp_user = setup["user"]
    stored_ftp_pass = setup["pass"]
    stored_chat_name = setup["chat"]
    stored_enc_pass = setup["enc"]
    stored_display_name = setup.get("display_name", setup["name"])

    username_entry.delete(0, "end")
    username_entry.insert(0, stored_display_name)
    modal_context.destroy()
    connect()


def delete_saved_setup(name, container, modal_context):
    global saved_setups
    saved_setups = [item for item in saved_setups if item["name"] != name]
    persist_saved_setups()
    render_saved_setups_popup(container, modal_context)


def open_saves_modal():
    modal = ctk.CTkToplevel(main)
    modal.title("Saved Profiles")
    modal.geometry("550x350")
    modal.resizable(False, False)
    modal.transient(main)
    modal.grab_set()
    modal.configure(fg_color=BG_MAIN)

    title_label = ctk.CTkLabel(
        modal,
        text="Saved Servers",
        font=("Segoe UI", 14, "bold"),
        text_color="#cbd5e1",
    )
    title_label.pack(pady=(15, 5))

    setups_container = ctk.CTkScrollableFrame(
        modal,
        fg_color=BG_CARD,
        border_width=1,
        border_color=COLOR_BORDER,
        corner_radius=12,
    )
    setups_container.pack(fill="both", expand=True, padx=20, pady=10)

    render_saved_setups_popup(setups_container, modal)


def render_saved_setups_popup(container, modal_context):
    for child in container.winfo_children():
        child.destroy()

    if not saved_setups:
        ctk.CTkLabel(
            container, text="No saved server configurations found.", text_color="gray"
        ).pack(pady=40)
        return

    for setup in saved_setups:
        row_frame = ctk.CTkFrame(
            container,
            fg_color=BG_INPUT,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        row_frame.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(
            row_frame,
            text=f"{setup['name']} ({setup.get('display_name')})",
            text_color="white",
            anchor="w",
        ).pack(side="left", padx=15, pady=8, fill="x", expand=True)

        ctk.CTkButton(
            row_frame,
            text="Save & Connect",
            font=("Segoe UI", 11, "bold"),
            width=110,
            height=28,
            fg_color=COLOR_GREEN,
            hover_color="#16a34a",
            command=lambda s=setup: direct_connect_profile(s, modal_context),
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            row_frame,
            text="Delete",
            font=("Segoe UI", 11),
            width=60,
            height=28,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda n=setup["name"]: delete_saved_setup(
                n, container, modal_context
            ),
        ).pack(side="right", padx=(5, 10))


def trigger_ui_update_alert(repo, tag):
    # Pure TK/CTK Standard UI Message Box
    messagebox.showinfo(
        "🚀 Update Available",
        f"A new release has been detected on GitHub!\n\nRepository: {repo}\nLatest Version: {tag}\n\nPlease update your application client.",
    )


def check_github_releases_loop():
    REPO = "ahmedomardev/FTPChat"
    API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

    CACHE_FILE = os.path.join(base_dir, "latest_release.json")

    try:
        with open(CACHE_FILE, "r") as f:
            last_seen = json.load(f).get("tag_name")
    except FileNotFoundError:
        last_seen = None

    while True:
        try:
            r = requests.get(API_URL, timeout=10)
            if r.status_code == 200:
                latest = r.json()["tag_name"]
                if latest != last_seen:
                    # Safely pushes the execution command into the main app thread loop
                    main.after(0, lambda: trigger_ui_update_alert(REPO, latest))

                    with open(CACHE_FILE, "w") as f:
                        json.dump({"tag_name": latest}, f)
                    last_seen = latest
        except Exception as e:
            print("Release Monitor Exception:", e)

        time.sleep(3600)


# *--- UI SETUP ---

main = ctk.CTk()
main.title("FTPChat")
main.geometry("1980x1080")
main.configure(fg_color=BG_MAIN)

top_card = ctk.CTkFrame(
    main, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=COLOR_BORDER
)
top_card.pack(fill="x", padx=15, pady=15)

top_row = ctk.CTkFrame(top_card, fg_color="transparent")
top_row.pack(fill="x", padx=15, pady=15)

ctk.CTkLabel(
    top_row,
    text="Username:",
    font=("Segoe UI", 12, "bold"),
    text_color="white",
).pack(side="left", padx=(5, 5))
username_entry = ctk.CTkEntry(
    top_row,
    fg_color=BG_INPUT,
    border_color=COLOR_BORDER,
    corner_radius=10,
    placeholder_text="Anonymous",
)
username_entry.pack(side="left", fill="x", expand=True, padx=5)

status_label = ctk.CTkLabel(
    top_row, text="Disconnected", text_color="gray", font=("Segoe UI", 12, "bold")
)
status_label.pack(side="right", padx=15)


def open_setup_modal():
    modal = ctk.CTkToplevel(main)
    modal.title("Configure New Server")
    modal.geometry("500x380")
    modal.resizable(False, False)
    modal.transient(main)
    modal.grab_set()
    modal.configure(fg_color=BG_MAIN)

    fields = [
        ("Profile Name:", "SETUP_NAME", None),
        ("Server IP / Hostname:", "STORED_FTP_HOST", None),
        ("Server Username:", "STORED_FTP_USER", None),
        ("Server Password:", "STORED_FTP_PASS", "*"),
        ("Chat Room File (.txt):", "STORED_CHAT_NAME", None),
        ("Encryption Password:", "STORED_ENC_PASS", "*"),
    ]
    entries = {}

    form = ctk.CTkFrame(
        modal,
        fg_color=BG_CARD,
        corner_radius=14,
        border_width=1,
        border_color=COLOR_BORDER,
    )
    form.pack(fill="both", expand=True, padx=15, pady=15)

    for idx, (label_text, attr, mask) in enumerate(fields):
        ctk.CTkLabel(form, text=label_text, text_color="#cbd5e1", anchor="w").grid(
            row=idx, column=0, padx=15, pady=8, sticky="w"
        )
        ent = ctk.CTkEntry(
            form,
            show=mask,
            fg_color=BG_INPUT,
            border_color=COLOR_BORDER,
            corner_radius=8,
            width=240,
        )
        ent.grid(row=idx, column=1, padx=15, pady=8, sticky="ew")

        if attr == "STORED_FTP_HOST" and stored_ftp_host:
            ent.insert(0, stored_ftp_host)
        if attr == "STORED_FTP_USER" and stored_ftp_user:
            ent.insert(0, stored_ftp_user)
        if attr == "STORED_FTP_PASS" and stored_ftp_pass:
            ent.insert(0, stored_ftp_pass)
        if attr == "STORED_CHAT_NAME" and stored_chat_name:
            ent.insert(0, stored_chat_name)
        if attr == "STORED_ENC_PASS" and stored_enc_pass:
            ent.insert(0, stored_enc_pass)
        entries[attr] = ent

    def on_save_profile():
        vals = {k: e.get().strip() for k, e in entries.items()}
        if not all(vals.values()):
            messagebox.showwarning(
                "Warning", "All parameters must be filled before committing data."
            )
            return

        global stored_ftp_host, stored_ftp_user, stored_ftp_pass, stored_chat_name, stored_enc_pass, stored_display_name
        stored_ftp_host = vals["STORED_FTP_HOST"]
        stored_ftp_user = vals["STORED_FTP_USER"]
        stored_ftp_pass = vals["STORED_FTP_PASS"]
        stored_chat_name = vals["STORED_CHAT_NAME"]
        stored_enc_pass = vals["STORED_ENC_PASS"]
        stored_display_name = username_entry.get().strip() or "Anonymous"

        new_profile = {
            "name": vals["SETUP_NAME"],
            "display_name": stored_display_name,
            "host": stored_ftp_host,
            "user": stored_ftp_user,
            "pass": stored_ftp_pass,
            "chat": stored_chat_name,
            "enc": stored_enc_pass,
        }

        global saved_setups
        saved_setups = [
            item for item in saved_setups if item["name"] != vals["SETUP_NAME"]
        ]
        saved_setups.append(new_profile)
        persist_saved_setups()
        modal.destroy()
        connect()

    btn_row = ctk.CTkFrame(modal, fg_color="transparent")
    btn_row.pack(fill="x", pady=(0, 15))
    ctk.CTkButton(
        btn_row,
        text="Save & Connect",
        fg_color=COLOR_BLUE,
        hover_color="#3b82f6",
        command=on_save_profile,
    ).pack(side="left", expand=True, padx=10)
    ctk.CTkButton(
        btn_row,
        text="Cancel",
        fg_color="#475569",
        hover_color="#334155",
        command=modal.destroy,
    ).pack(side="left", expand=True, padx=10)


ctk.CTkButton(
    top_row,
    text="Saves",
    fg_color="#334155",
    hover_color="#1e293b",
    corner_radius=10,
    width=150,
    command=open_saves_modal,
).pack(side="right", padx=5)

ctk.CTkButton(
    top_row,
    text="Setup",
    fg_color=COLOR_BLUE,
    hover_color="#3b82f6",
    corner_radius=10,
    width=120,
    command=open_setup_modal,
).pack(side="right", padx=5)

disconnect_button = ctk.CTkButton(
    top_row,
    text="Disconnect",
    fg_color="#ef4444",
    hover_color="#dc2626",
    corner_radius=10,
    width=140,
    command=disconnect_handler,
)

# *Chat Display Card Area
ctk.CTkLabel(main, text="Chat", font=("Segoe UI", 12, "bold"), text_color="white").pack(
    anchor="w", padx=20, pady=(5, 2)
)

chat_card = ctk.CTkFrame(
    main, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=COLOR_BORDER
)
chat_card.pack(fill="both", expand=True, padx=15, pady=5)

chat_display = ctk.CTkTextbox(
    chat_card,
    fg_color=BG_INPUT,
    border_color=COLOR_BORDER,
    text_color="#e2e8f0",
    font=("Consolas", 12),
    corner_radius=14,
)
chat_display.pack(fill="both", expand=True, padx=10, pady=10)
chat_display.configure(state="disabled")

# *Message Input Card Area
ctk.CTkLabel(
    main,
    text="Write your message below:",
    font=("Segoe UI", 12, "bold"),
    text_color="white",
).pack(anchor="w", padx=20, pady=(10, 2))

msg_card = ctk.CTkFrame(
    main, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=COLOR_BORDER
)
msg_card.pack(fill="x", padx=15, pady=(5, 15))

message_widget = ctk.CTkTextbox(
    msg_card,
    height=70,
    fg_color=BG_INPUT,
    border_color=COLOR_BORDER,
    text_color="white",
    font=("Segoe UI", 12),
    corner_radius=14,
)
message_widget.pack(fill="x", side="top", padx=10, pady=(10, 5))

send_button = ctk.CTkButton(
    msg_card,
    text="Send Message",
    height=30,
    fg_color=COLOR_BLUE,
    hover_color="#3b82f6",
    corner_radius=14,
    font=("Segoe UI", 13, "bold"),
    command=lambda: send_messages(
        username_entry.get().strip() or "Anonymous", message_widget.get("1.0", "end-1c")
    ),
)
send_button.pack(fill="x", side="top", padx=10, pady=(0, 10))


def send_handler_event(event):
    send_button.invoke()
    return "break"


message_widget.bind("<Return>", send_handler_event)

load_saved_setups()

# Launch the release listener inside a non-blocking background daemon thread
Thread(target=check_github_releases_loop, daemon=True).start()

main.mainloop()
