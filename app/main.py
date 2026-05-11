import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from snaptrade_client import SnapTrade
from concurrent.futures import ThreadPoolExecutor, as_completed

if getattr(sys, 'frozen', False):
    EXE_DIR    = Path(sys.executable).parent   # folder containing portfolio.exe
    BUNDLE_DIR = Path(sys._MEIPASS)            # temp folder with bundled files
else:
    EXE_DIR    = Path(__file__).parent.parent
    BUNDLE_DIR = Path(__file__).parent.parent

load_dotenv(EXE_DIR / "secret" / ".env")

app = FastAPI()

FRONTEND = BUNDLE_DIR / "frontend"

snaptrade = SnapTrade(
    client_id=os.environ["SNAPTRADE_CLIENT_ID"],
    consumer_key=os.environ["SNAPTRADE_CONSUMER_KEY"],
)
USER_ID     = os.environ["SNAPTRADE_USER_ID"]
USER_SECRET = os.environ["SNAPTRADE_USER_SECRET"]

OWNER_MAP = {
    "19e75b0c-8369-42c3-880c-6e760d633cdc": "Rej",
    "28ea0638-716a-4f61-b0bc-21425da12c04": "Kaz",
}

def fetch_holdings(account):
    h = snaptrade.account_information.get_user_holdings(
        user_id=USER_ID, user_secret=USER_SECRET, account_id=account["id"]
    ).body
    positions = []
    for p in h.get("positions", []):
        brok_sym = p.get("symbol", {}) or {}
        univ_sym = (brok_sym.get("symbol", {}) or {}) if isinstance(brok_sym, dict) else {}
        if not isinstance(univ_sym, dict):
            univ_sym = {}
        ticker = univ_sym.get("raw_symbol") or univ_sym.get("symbol", "")
        currency = (univ_sym.get("currency", {}) or {}).get("code", "")
        description = p.get("description") or univ_sym.get("description", "")
        positions.append({
            "ticker":       ticker,
            "description":  description,
            "currency":     currency,
            "units":        p.get("units"),
            "price":        p.get("price"),
            "market_value": round((p.get("units") or 0) * (p.get("price") or 0), 2),
        })
    return {
        "id":       account["id"],
        "owner":    OWNER_MAP.get(account["brokerage_authorization"], "Unknown"),
        "name":     account["name"],
        "number":   account["number"],
        "balance":  account["balance"]["total"]["amount"],
        "currency": account["balance"]["total"]["currency"],
        "positions": sorted(positions, key=lambda x: x["market_value"], reverse=True),
    }

@app.get("/api/portfolio")
def get_portfolio():
    accounts = snaptrade.account_information.list_user_accounts(
        user_id=USER_ID, user_secret=USER_SECRET
    ).body
    results = []
    with ThreadPoolExecutor() as pool:
        futures = {pool.submit(fetch_holdings, a): a for a in accounts}
        for f in as_completed(futures):
            results.append(f.result())
    results.sort(key=lambda x: (x["owner"], x["name"]))
    total = sum(a["balance"] for a in results)
    return {"accounts": results, "total_cad": round(total, 2)}

app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
