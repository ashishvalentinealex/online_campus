import yagmail
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "newcomers_final.xlsx"
SENDER     = os.getenv("SENDER_EMAIL")
PASSWORD   = os.getenv("SENDER_PASSWORD")
DATE       = datetime.datetime.now().strftime("%d-%m-%Y")

COORDINATORS = {
    "Deepshika": "deepshika.dolly186@gmail.com",
    "Suneela":   "suneelakandimalla@gmail.com",
    "Ashish":    "avation2k14@gmail.com",
}

def send_allocation_emails(filepath=INPUT_FILE):
    df = pd.read_excel(filepath)

    groups = {
        "Deepshika": df[df["Continent"].str.strip().str.lower() == "africa"],
        "Suneela":   df[df["Continent"].str.strip().str.lower() == "europe"],
        "Ashish":    df[~df["Continent"].str.strip().str.lower().isin(["africa", "europe"])],
    }

    yag = yagmail.SMTP(user=SENDER, password=PASSWORD)

    for name, members in groups.items():
        if members.empty:
            print(f"⏭️  No members for {name}, skipping.")
            continue

        table = members.to_html(index=False)
        body = f"""
        <html><body>
            <h2 style="color:#333;">New Member Allocation — {DATE}</h2>
            <p>Hi {name}, please find your allocated new members below:</p>
            {table}
            <br><b>Steve Patta</b><br>
            <b>E-Church Director, TKT Church.</b>
        </body></html>
        """
        yag.send(
            to=COORDINATORS[name],
            subject=f"New Member Allocation for {name} — {DATE}",
            contents=[body],
        )
        print(f"✅ Allocation email sent to {name} ({COORDINATORS[name]}) — {len(members)} member(s)")

if __name__ == "__main__":
    send_allocation_emails()
