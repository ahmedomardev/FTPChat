"""
*Version: 2.1
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
- **Commercial use of this software requires prior written permission from the author.** r
- **The author reserves the right to relicense this software as closed-source or commercial at any time.**
- All rights to the name “FTPChat” and its protocol specification are retained by Ahmed Omar Saad.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Notes:
The author may offer separate commercial licenses for enterprise or closed-source use. Contact <ahmedomardev@outlook.com> for inquiries.
This license applies to all source code, documentation, and protocol specifications included in the FTPChat project.
"""

from tkinter import messagebox
import os

import customtkinter as ctk
from functions import connect
from functions import disconnect
from functions import send_messages
from functions import init_app
from functions import load_saved_setups
from functions import render_saved_setups
from functions import save_setup_entry
from functions import stored_ftp_host
from functions import stored_ftp_user
from functions import stored_ftp_pass
from functions import stored_chat_name
from functions import stored_enc_pass
from functions import stored_display_name
from functions import stored_ignore_notifications
from functions import CONNECTED
from functions import minimize_to_tray
from functions import disconnect_button

# *--- UI SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

main = ctk.CTk()
main.title("FTPChat")
main.geometry("1920x1080")
main.state("zoomed")
main.configure(fg_color="#0f1720")
main.grid_rowconfigure(0, weight=1)
main.grid_columnconfigure(0, weight=1)


saved_setups = []


def minimize_to_tray():
    return minimize_to_tray()


def change_theme(theme_name):
    """Changes the application appearance mode."""
    ctk.set_appearance_mode(theme_name)
    messagebox.showinfo("Theme Changed", f"Appearance mode changed to {theme_name}.")


def open_setup_modal(save_only: bool = False):
    """Opens the setup modal for entering FTP and encryption details."""
    modal = ctk.CTkToplevel(main)
    modal.title("Setup connection")
    modal.geometry("490x490")
    modal.resizable(False, False)
    modal.transient(main)
    modal.grab_set()
    modal.configure(fg_color="#0f1720")
    modal.grid_columnconfigure(1, weight=1)

    form_frame = ctk.CTkFrame(
        modal,
        fg_color="#111827",
        corner_radius=20,
        border_width=1,
        border_color="#1e293b",
    )
    form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    form_frame.grid_columnconfigure(1, weight=1)

    label_fg = "white"
    entry_fg = "#0f1720"
    entry_border = "#334155"
    entry_radius = 14

    ctk.CTkLabel(form_frame, text="Save name:", anchor="w", text_color=label_fg).grid(
        row=0, column=0, padx=16, pady=10, sticky="w"
    )
    setup_name_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        placeholder_text="Home Chat",
    )
    setup_name_entry.grid(row=0, column=1, padx=(0, 16), pady=10, sticky="ew")

    ctk.CTkLabel(
        form_frame, text="Display Name:", anchor="w", text_color=label_fg
    ).grid(row=1, column=0, padx=16, pady=10, sticky="w")
    display_name_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        placeholder_text="Your name",
    )
    display_name_entry.grid(row=1, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_display_name:
        display_name_entry.insert(0, stored_display_name)

    ctk.CTkLabel(form_frame, text="Host:", anchor="w", text_color=label_fg).grid(
        row=2, column=0, padx=16, pady=10, sticky="w"
    )
    host_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        placeholder_text="ftps.example.com",
    )
    host_entry.grid(row=2, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_ftp_host:
        host_entry.insert(0, stored_ftp_host)

    ctk.CTkLabel(form_frame, text="FTP User:", anchor="w", text_color=label_fg).grid(
        row=3, column=0, padx=16, pady=10, sticky="w"
    )
    user_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        placeholder_text="ftp_user",
    )
    user_entry.grid(row=3, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_ftp_user:
        user_entry.insert(0, stored_ftp_user)

    ctk.CTkLabel(form_frame, text="Password:", anchor="w", text_color=label_fg).grid(
        row=4, column=0, padx=16, pady=10, sticky="w"
    )
    passwd_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        show="*",
    )
    passwd_entry.grid(row=4, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_ftp_pass:
        passwd_entry.insert(0, stored_ftp_pass)

    ctk.CTkLabel(form_frame, text="Chat File:", anchor="w", text_color=label_fg).grid(
        row=5, column=0, padx=16, pady=10, sticky="w"
    )
    chat_name_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        placeholder_text="chatroom",
    )
    chat_name_entry.grid(row=5, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_chat_name:
        chat_name_entry.insert(0, stored_chat_name)

    ctk.CTkLabel(
        form_frame, text="Encryption Key:", anchor="w", text_color=label_fg
    ).grid(row=6, column=0, padx=16, pady=10, sticky="w")
    enc_pass_entry = ctk.CTkEntry(
        form_frame,
        fg_color=entry_fg,
        border_color=entry_border,
        corner_radius=entry_radius,
        show="*",
    )
    enc_pass_entry.grid(row=6, column=1, padx=(0, 16), pady=10, sticky="ew")
    if stored_enc_pass:
        enc_pass_entry.insert(0, stored_enc_pass)

    ignore_var = ctk.BooleanVar(value=bool(stored_ignore_notifications))
    ctk.CTkLabel(
        form_frame,
        text="Ignore Notifications:",
        anchor="w",
        text_color=label_fg,
    ).grid(row=7, column=0, padx=16, pady=10, sticky="w")
    ignore_cb = ctk.CTkCheckBox(
        form_frame,
        variable=ignore_var,
        text="Do not show notifications for this setup",
    )
    ignore_cb.grid(row=7, column=1, padx=(0, 16), pady=10, sticky="w")

    def store_values():
        setup_name = setup_name_entry.get().strip()
        display_name = display_name_entry.get().strip()
        host = host_entry.get().strip()
        user = user_entry.get().strip()
        passwd = passwd_entry.get().strip()
        chat_name = chat_name_entry.get().strip()
        enc_pass = enc_pass_entry.get().strip()

        if not (
            setup_name
            or display_name
            or host
            or user
            or passwd
            or chat_name
            or enc_pass
        ):
            messagebox.showwarning(
                "Warning", "Please fill in all setup fields before continuing"
            )
            return None
        return setup_name, display_name

    def on_connect():
        result = store_values()
        if not result:
            return
        modal.destroy()
        connect()
        status_label.configure(text="Connected", text_color="green")
        if disconnect_button is not None:
            disconnect_button.configure(state="normal")
        update_sidebar_connect_button(CONNECTED)

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

    ctk.CTkButton(
        buttons,
        text="Cancel",
        command=modal.destroy,
        fg_color="#475569",
    ).grid(row=0, column=0, sticky="ew", padx=(0, 10))
    ctk.CTkButton(
        buttons,
        text="Save",
        command=on_save,
        fg_color="#38bdf8",
    ).grid(row=0, column=1, sticky="ew", padx=(0, 10))

    if save_only:
        ctk.CTkButton(
            buttons,
            text="Done",
            command=modal.destroy,
            fg_color="#60a5fa",
        ).grid(row=0, column=2, sticky="ew")
    else:
        ctk.CTkButton(
            buttons,
            text="Connect",
            command=on_connect,
            fg_color="#60a5fa",
        ).grid(row=0, column=2, sticky="ew")


app_frame = ctk.CTkFrame(main, fg_color="#111827", corner_radius=30, border_width=0)
app_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
app_frame.grid_rowconfigure(0, weight=1)
app_frame.grid_columnconfigure(0, weight=0)
app_frame.grid_columnconfigure(1, weight=1)

sidebar = ctk.CTkFrame(
    app_frame,
    fg_color="#111827",
    corner_radius=24,
    border_width=1,
    border_color="#1e293b",
)
sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=0)
sidebar.grid_rowconfigure(5, weight=1)
sidebar.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(
    sidebar,
    text="FTPChat",
    font=("Segoe UI Variable", 24, "bold"),
    text_color="white",
).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 4))

ctk.CTkLabel(
    sidebar,
    text="",
    font=("Segoe UI Variable", 12),
    text_color="#94a3b8",
).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 20))

button_bar = ctk.CTkFrame(sidebar, fg_color="transparent")
button_bar.grid(row=2, column=0, sticky="ew", padx=24)
button_bar.grid_columnconfigure(0, weight=1)
button_bar.grid_columnconfigure(1, weight=1)
button_bar.grid_columnconfigure(2, weight=1)

sidebar_connect_button = None


def sidebar_connect_action():
    connect()
    update_sidebar_connect_button(CONNECTED)


def update_sidebar_connect_button(connected: bool):
    global sidebar_connect_button
    if sidebar_connect_button is None:
        return
    if connected:
        sidebar_connect_button.configure(
            text="Disconnect",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: safe_disconnect(),
        )
    else:
        sidebar_connect_button.configure(
            text="Connect",
            fg_color="#22c55e",
            hover_color="#16a34a",
            command=sidebar_connect_action,
        )


ctk.CTkButton(
    button_bar,
    text="Setup",
    fg_color="#60a5fa",
    hover_color="#3b82f6",
    command=open_setup_modal,
).grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(0, 16))

sidebar_connect_button = ctk.CTkButton(
    button_bar,
    text="Connect",
    fg_color="#22c55e",
    hover_color="#16a34a",
    command=sidebar_connect_action,
)
sidebar_connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 16))

try:
    update_sidebar_connect_button(CONNECTED)
except Exception:
    pass

ctk.CTkLabel(
    sidebar,
    text="Saved servers",
    font=("Segoe UI Variable", 14, "bold"),
    text_color="white",
).grid(row=3, column=0, sticky="w", padx=24, pady=(0, 8))

saved_setups_container = ctk.CTkScrollableFrame(
    sidebar,
    fg_color="#0f1720",
    border_width=1,
    border_color="#334155",
    corner_radius=20,
    height=440,
)
saved_setups_container.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 24))
saved_setups_container.grid_columnconfigure(0, weight=1)

chat_panel = ctk.CTkFrame(
    app_frame,
    fg_color="#0f1720",
    corner_radius=24,
    border_width=1,
    border_color="#1e293b",
)
chat_panel.grid(row=0, column=1, sticky="nsew")
chat_panel.grid_rowconfigure(3, weight=1)
chat_panel.grid_columnconfigure(0, weight=1)

chat_header = ctk.CTkFrame(
    chat_panel,
    fg_color="#111827",
    corner_radius=24,
    border_width=1,
    border_color="#1e293b",
)
chat_header.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
chat_header.grid_columnconfigure(0, weight=1)
chat_header.grid_columnconfigure(1, weight=0)

chat_title = ctk.CTkLabel(
    chat_header,
    text="Conversation",
    font=("Segoe UI Variable", 22, "bold"),
    text_color="white",
)
chat_title.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=(20, 4))

status_label = ctk.CTkLabel(
    chat_header,
    text="Disconnected",
    font=("Segoe UI Variable", 12),
    text_color="#94a3b8",
)
status_label.grid(row=1, column=0, sticky="w", padx=(20, 0), pady=(0, 20))

chat_display = ctk.CTkTextbox(
    chat_panel,
    corner_radius=24,
    border_width=1,
    border_color="#334155",
    fg_color="#0b1720",
    text_color="white",
    height=240,
)
chat_display.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
chat_display.configure(state="disabled")
chat_display.see("end")

message_card = ctk.CTkFrame(
    chat_panel,
    fg_color="#111827",
    corner_radius=24,
    border_width=1,
    border_color="#334155",
)
message_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
message_card.grid_columnconfigure(0, weight=1)
message_card.grid_columnconfigure(1, weight=0)

ctk.CTkLabel(
    message_card,
    text="Message",
    font=("Segoe UI Variable", 12, "bold"),
    text_color="#cbd5e1",
).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

message_widget = ctk.CTkTextbox(
    message_card,
    height=200,
    corner_radius=18,
    border_width=2,
    border_color="#334155",
    fg_color="#0b1720",
    text_color="white",
)
message_widget.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
message_widget.see("end")

send_button = ctk.CTkButton(
    message_card,
    text="Send",
    height=35,
    fg_color="#60a5fa",
    hover_color="#3b82f6",
    font=("Segoe UI Variable", 13, "bold"),
    command=lambda: threaded_send(message_widget.get("1.0", "end-1c")),
)
send_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 16))


def threaded_send(message: str):
    """Send message in a background thread to avoid blocking the UI."""
    text = message.strip()
    if not text:
        return

    display_name = stored_display_name or "Anonymous"
    send_messages(display_name, text)


def safe_disconnect():
    """Call disconnect() with error handling and update UI."""
    disconnect()
    status_label.configure(text="Disconnected", text_color="gray")
    update_sidebar_connect_button(False)


def _on_return(event=None):
    threaded_send(message_widget.get("1.0", "end-1c"))
    return "break"


def _keep_scrolling():
    chat_display.see("end")
    main.after(1000, _keep_scrolling)


try:
    load_saved_setups()
    render_saved_setups()
except Exception:
    pass

init_app(
    main,
    chat_display,
    message_widget,
    send_button,
    None,
    status_label,
    None,
    saved_setups_container,
    chat_title,
    os.path.join(os.path.dirname(__file__), "saved_setups.json"),
)

_keep_scrolling()


def on_close():
    should_minimize = messagebox.askyesno(
        "Exit FTPChat",
        "Minimize to tray and keep fetching messages?\n\nYes = Minimize to tray (keep running)\nNo = Close FTPChat",
    )
    if should_minimize:
        minimize_to_tray()
        return
    main.destroy()


main.protocol("WM_DELETE_WINDOW", on_close)
main.bind("<Return>", _on_return)
main.mainloop()
