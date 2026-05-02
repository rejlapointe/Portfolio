import os
import tkinter as tk
import subprocess
import webbrowser
from dotenv import load_dotenv
from snaptrade_client import SnapTrade

load_dotenv(os.path.join(os.path.dirname(__file__), "secret", ".env"))
CLIENT_ID    = os.environ["SNAPTRADE_CLIENT_ID"]
CONSUMER_KEY = os.environ["SNAPTRADE_CONSUMER_KEY"]
USER_ID      = os.environ["SNAPTRADE_USER_ID"]
USER_SECRET  = os.environ["SNAPTRADE_USER_SECRET"]

snaptrade = SnapTrade(client_id=CLIENT_ID, consumer_key=CONSUMER_KEY)

def connect(label):
    status.config(text=f"Generating link for {label}...", fg="gray")
    root.update()
    try:
        login = snaptrade.authentication.login_snap_trade_user(
            user_id=USER_ID,
            user_secret=USER_SECRET,
            broker="QUESTRADE",
            connection_type="read",
        )
        uri = login.body.get("redirectURI") or login.body.get("loginLink")
        if label == "Wife":
            # Open in InPrivate so her Questrade login isn't mixed with yours
            subprocess.Popen([
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "--inprivate", uri
            ])
            status.config(text="InPrivate window opened for Wife. Have her log into her Questrade account.", fg="green")
        else:
            webbrowser.open(uri)
            status.config(text="Browser opened for Rej. Complete the login there.", fg="green")
    except Exception as e:
        status.config(text=f"Error: {e}", fg="red")

root = tk.Tk()
root.title("Connect Questrade Accounts")
root.geometry("420x160")
root.resizable(False, False)

tk.Label(root, text="Click to connect each Questrade account", font=("Segoe UI", 11)).pack(pady=(18, 10))

btn_frame = tk.Frame(root)
btn_frame.pack()
tk.Button(btn_frame, text="Connect Rej's Account",  width=20, height=2,
          command=lambda: connect("Rej")).pack(side="left", padx=12)
tk.Button(btn_frame, text="Connect Wife's Account", width=20, height=2,
          command=lambda: connect("Wife")).pack(side="left", padx=12)

status = tk.Label(root, text="", font=("Segoe UI", 9), wraplength=380)
status.pack(pady=12)

root.mainloop()
