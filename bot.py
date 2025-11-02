import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re

# --- CONFIG ---
BOT_TOKEN = "8482260721:AAEmyxKMGwmJu4xP7hH_PLFcAzSP3BhO8hA"
CHAT_ID = "8553776330"
MENU_URL = "https://www.akbild.ac.at/de/universitaet/services/menueplan"
TZ = pytz.timezone("Europe/Vienna")

WEEKDAYS = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
}


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)


def fetch_html():
    r = requests.get(MENU_URL, timeout=10)
    r.raise_for_status()
    return r.text


def parse_today(html, weekday_name):
    # Convert HTML to text
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n", strip=True)

    # Pattern: find the weekday and capture until next weekday or end
    pattern = rf"{weekday_name}(.*?)(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|$)"
    m = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)

    if m:
        # Clean whitespace
        return m.group(1).strip()

    return None


def main():
    today = datetime.now(TZ)
    weekday = today.weekday()

    if weekday > 4:  # Weekend
        send_telegram("Heute gibt es kein Mensa-Menü (Wochenende). ✅")
        return

    weekday_name = WEEKDAYS[weekday]

    html = fetch_html()
    menu = parse_today(html, weekday_name)

    if menu:
        send_telegram(f"🍽 {weekday_name}:\n\n{menu}")
    else:
        send_telegram("Kein Menü gefunden (noch nicht veröffentlicht oder Feiertag?). 🤷")


if __name__ == "__main__":
    main()
