"""
FTPChat - Encrypted FTP-based Messaging Protocol
Version 1.6 — February 2026
Type: Custom-styled MIT LICENSE
Author: Ahmed Omar Saad
Contact: ahmedomardev@outlook.com
FTPChat  © 2025/5/20 by Ahmed Omar Saad is licensed under CC BY-NC-SA 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/4.0/

*Permission is hereby granted, free of charge, to any person obtaining a copy
*of this software and associated documentation files (the “Software”), to deal
*in the Software without restriction, including without limitation the rights
*to use, copy, modify, merge, publish, distribute, and/or sublicense copies of
*the Software, subject to the following conditions:

*- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*- **Commercial use of this software requires prior written permission from the author.**
*- **The author reserves the right to relicense this software as closed-source or commercial at any time.**
*- All rights to the name “FTPChat” and its project specification are retained by Ahmed Omar Saad.

*THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
*INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
*AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
*DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
*OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*Notes:
*The author may offer separate commercial licenses for enterprise or closed-source use. Contact ahmedomardev@outlook.com for inquiries.
*This license applies to all source code, documentation, and project specifications included in the FTPChat project.
"""
import base64
from datetime import datetime
from ftplib import FTP, FTP_TLS
from threading import Thread
from tkinter import DISABLED, NORMAL, messagebox
from tkinter.scrolledtext import ScrolledText
from webbrowser import open as open_link
from zlib import compress, decompress

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ttkbootstrap import Button, Entry, Label, Menu, StringVar, Window


def help_func():
    open_link("ahmed-omar-software-projects.mydurable.com")


SALT = b'q6334#Q0q8294%E$(#$%^&^%$#@!#%^YHB>$W#CX>E'


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(text: str) -> str:
    password = encryption_pass.get()
    key = derive_key(password, SALT)
    f = Fernet(key)
    compressed = compress(text.encode("utf-8"))
    encrypted = f.encrypt(compressed)
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt(text: str) -> str:
    password = encryption_pass.get()
    key = derive_key(password, SALT)
    f = Fernet(key)
    encrypted = base64.b64decode(text.encode("utf-8"))
    decrypted = f.decrypt(encrypted)
    decompressed = decompress(decrypted)
    return decompressed.decode("utf-8")


# !---The sending and reading messages functions---


def send_message_non(username, message):
    msg = encrypt(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}:{username}: {message}")
    ftp_host = FTP_HOST.get()
    ftp_user = FTP_USER.get()
    ftp_pass = FTP_PASS.get()
    chat_name = f"{chat_file_name.get()}.txt"
    local_temp = "chat_temp.txt"

    try:
        try:
            ftp = FTP_TLS(ftp_host)
            ftp.login(ftp_user, ftp_pass)
        except Exception:
            ftp = FTP(ftp_host)
            ftp.login(ftp_user, ftp_pass)

        try:
            with open(local_temp, "wb") as f:
                ftp.retrbinary(f"RETR " + chat_name, f.write)
        except Exception:
            pass

        with open(local_temp, "w", encoding="utf-8") as f:
            f.write(f"{msg}\n")

        with open(local_temp, "rb") as f:
            ftp.storbinary(f"APPE " + chat_name, f)

        ftp.quit()
        read_messages()

    except Exception as error:
        messagebox.showerror("Error sending message", str(error))


def send_messages(username, message):
    Thread(target=send_message_non, args=(
        username, message), daemon=True).start()


def read_messages_non():
    ftp_host = FTP_HOST.get()
    ftp_user = FTP_USER.get()
    ftp_pass = FTP_PASS.get()
    chat_name = f"{chat_file_name.get()}.txt"
    local_temp = "chat_temp.txt"

    try:
        try:
            ftp = FTP_TLS(ftp_host)
            ftp.login(ftp_user, ftp_pass)
        except Exception as e:
            print(f"FTPS failed ({e}), falling back to FTP...")
            ftp = FTP(ftp_host)
            ftp.login(ftp_user, ftp_pass)

        with open(local_temp, "wb") as file:
            ftp.retrbinary(f"RETR {chat_name}", file.write)
        ftp.quit()

        with open(local_temp, "r", encoding="utf-8") as file:
            lines = file.readlines()

        out_lines = []
        for line in lines:
            try:
                out_lines.append(decrypt(line.strip()))
            except Exception:
                out_lines.append(line.strip())

        message_text = "\n".join(
            out_lines) if out_lines else "No messages yet."

        chat_notes.config(state=NORMAL)
        chat_notes.delete("1.0", "end")
        chat_notes.insert("end", message_text)
        chat_notes.see("end")
        chat_notes.config(state=DISABLED)

    except Exception as error:
        messagebox.showerror("Error reading messages", str(error))


def read_messages():
    Thread(target=read_messages_non, daemon=True).start()


def auto_refresh_func():
    if FTP_HOST.get() and FTP_USER.get() and FTP_PASS.get() and chat_file_name.get() and encryption_pass.get():
        read_messages()
        main.after(5000, auto_refresh_func)
    else:
        messagebox.showwarning("Warning", "Please, fill in all details")


def start_loop():
    auto_refresh_func()
    done_butt.config(state=DISABLED)
    done_butt.config(text="Loop Started")


main = Window(themename="darkly")
main.title("FTPChat")
main.geometry("1920x1080")
main.state("zoomed")
menubar = Menu(main)
main.config(menu=menubar)

# Menubar
accessibility_menu = Menu(menubar, tearoff=False)
accessibility_menu.add_command(label="Help", command=help_func)
accessibility_menu.add_command(label="Exit", command=lambda: main.destroy())
menubar.add_cascade(label="Accessibility", menu=accessibility_menu)

# Widgets

FTP_HOST = StringVar()
Label(main, text="Host:").place(x=5, y=5)
Entry(main, textvariable=FTP_HOST, width=225).place(x=100, y=5)

FTP_USER = StringVar()
Label(main, text="FTP User:").place(x=5, y=40)
Entry(main, textvariable=FTP_USER, width=225).place(x=100, y=40)

FTP_PASS = StringVar()
Label(main, text="Password:").place(x=5, y=75)
Entry(main, textvariable=FTP_PASS, width=225, show="*").place(x=100, y=75)

username_var = StringVar()
Label(main, text="Username:").place(x=5, y=110)
Entry(main, textvariable=username_var, width=225).place(x=100, y=110)

encryption_pass = StringVar()
Label(main, text="Password:").place(x=5, y=146)
Entry(main, textvariable=encryption_pass,
      width=225, show="*").place(x=100, y=146)

chat_file_name = StringVar()
Label(main, text="Chat File:").place(x=5, y=181)
Entry(main, textvariable=chat_file_name, width=201).place(x=100, y=181)

done_butt = Button(
    main,
    text="Done",
    command=lambda: start_loop(),
    width=20
)
done_butt.place(x=1730, y=181)


Label(main, text="Chat:").place(x=5, y=215)
chat_notes = ScrolledText(main, width=233, height=15)
chat_notes.place(x=5, y=245)
chat_notes.see("end")
chat_notes.config(state=DISABLED)

Label(main, text="Message:").place(x=5, y=560)
msg = ScrolledText(main, width=233, height=15)
msg.place(x=5, y=590)

send_butt = Button(
    main,
    text="Send",
    command=lambda: send_messages(username_var.get(), msg.get("1.0", "end")),
    width=235,
).place(x=5, y=915)


main.mainloop()
