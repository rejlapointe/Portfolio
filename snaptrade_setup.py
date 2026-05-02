"""
SnapTrade setup: generate Questrade connection portal links for Rej and wife.
One SnapTrade user holds both Questrade connections.

Run this, then open each link in a browser and log in with the respective
Questrade account. Each link expires in 5 minutes — open Rej's first,
complete it, then run again (or scroll down) for wife's link.
"""

import os
from dotenv import load_dotenv
from snaptrade_client import SnapTrade

load_dotenv()
CLIENT_ID    = os.environ["SNAPTRADE_CLIENT_ID"]
CONSUMER_KEY = os.environ["SNAPTRADE_CONSUMER_KEY"]
USER_ID      = os.environ["SNAPTRADE_USER_ID"]
USER_SECRET  = os.environ["SNAPTRADE_USER_SECRET"]

snaptrade = SnapTrade(client_id=CLIENT_ID, consumer_key=CONSUMER_KEY)

for label in ["Rej", "Wife"]:
    login = snaptrade.authentication.login_snap_trade_user(
        user_id=USER_ID,
        user_secret=USER_SECRET,
        broker="QUESTRADE",
        connection_type="read",
    )
    uri = login.body.get("redirectURI") or login.body.get("loginLink")
    print(f"[{label}] Questrade connection link (open in browser, expires in 5 min):")
    print(f"  {uri}\n")
