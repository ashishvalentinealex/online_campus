import yagmail
import os
import pandas as pd
import re
from tabulate import tabulate
import datetime

current_date = datetime.datetime.now().strftime("%d-%m-%Y")

# --- Config ---
EXCEL_PATH = r"C:\Users\avati\Documents\E-CHURCH\NewMembers.xlsx"
IMAGE_PATH = r"C:\Users\avati\Documents\E-CHURCH\logo.png"
PDF_PATH   = r"C:\Users\avati\Documents\E-CHURCH\welcome.pdf"
SENDER     = "efamcare@gmail.com"
PASSWORD   = "evkzzjrlkbepxqsm"

COORDINATORS = {
    "Suneela":   "suneelakandimalla@gmail.com",
    "Deepshika": "deepshika.dolly186@gmail.com",
    "Arulya":    "arulyasoni28@gmail.com",
    "Ashish":    "avation2k14@gmail.com",
    "Sam":       "samsuper301@gmail.com",
}

# --- Load & prepare data ---
df = pd.read_excel(EXCEL_PATH, header=None, names=["Email", "Name", "Place", "Number", "Country", "Continent"])
df["Number"] = df["Number"].apply(lambda x: re.sub(r"\D", "", str(x)))
df["WhatsApp Direct link"] = df["Number"].apply(
    lambda x: f"https://api.whatsapp.com/send/?phone={x}&text&type=phone_number&app_absent=0"
)

europe_members = df[df["Continent"] == "Europe"]
df = df[df["Continent"] != "Europe"].sample(frac=1).reset_index(drop=True)

# --- Assign members ---
assignments = {}
others = [c for c in COORDINATORS if c != "Suneela"]
for i, (_, row) in enumerate(df.iterrows()):
    coord = others[i % len(others)]
    assignments.setdefault(coord, []).append(row.to_dict())
assignments["Suneela"] = europe_members.to_dict("records")

# --- Send emails ---
yag = yagmail.SMTP(user=SENDER, password=PASSWORD)

for coordinator, members in assignments.items():
    table = tabulate(members, headers="keys", tablefmt="html")
    contents = [
        f"""
        <html><body>
            <img src="cid:logo.png" width="150"><br>
            <h1 style="color:#333333;">New Member Allocation</h1>
            <p style="font-size:16px; color:#333333;">
                Please find below the details of new members allocated to you:
            </p>
            {table}
            <br><b>Steve Patta</b><br>
            <b>E-Church Director, TKT Church.</b>
        </body></html>
        """,
        yagmail.inline(IMAGE_PATH),
        PDF_PATH,
    ]
    yag.send(
        to=COORDINATORS[coordinator],
        subject=f"New Member Allocation for {coordinator} for {current_date}",
        contents=contents,
    )
    print(f"Email sent to {COORDINATORS[coordinator]}!")
