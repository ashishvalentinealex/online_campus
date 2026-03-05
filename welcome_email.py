import re
import os
import yagmail
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
IMAGE_PATH   = os.getenv("IMAGE_PATH")
SENDER       = os.getenv("SENDER_EMAIL")
PASSWORD     = os.getenv("SENDER_PASSWORD")
RESIZED_PATH = "/tmp/TKT_CHURCH.jpeg"

SUBJECT_TEMPLATE = "Welcome to TKT Online Campus, {first_name}! 🌍"

BODY_TEMPLATE = """
<html>
<body style="font-family:Arial,sans-serif;font-size:15px;color:#222;line-height:1.6;margin:0;padding:16px;">
Dear {first_name},<br><br>
Warm greetings from the <strong>TKT Online Campus</strong>, on behalf of Bishop Samuel Patta and Ps. Merlyn Patta.<br><br>
We are so glad you are here. <strong>Welcome to the family!</strong> 🙏<br><br>
You are now part of a global community of believers — united not by geography, but by faith. Every week, brothers and sisters from across the world come together in our <strong>Online Community Meetings</strong> to worship, pray, and grow in the Word of God.<br><br>
These are not just meetings — they are moments where faith is strengthened, burdens are lifted, and lives are transformed. Together, we encourage one another, hold each other accountable, and help each other stay rooted in our walk with God.<br><br>
All meetings are held on <strong>Zoom</strong> and are completely <strong>free</strong>.<br><br>
📲 <strong>You will soon receive a WhatsApp message from our official number: +91 90000 33551</strong><br>
It will include a link to join our community group — please do join it! We share daily encouragement, fellowship meeting links, and much more to keep you inspired in your walk with God.<br><br>
To know more about us, visit our YouTube channel:<br>
<a href="https://www.youtube.com/@tktchurchofficial">https://www.youtube.com/@tktchurchofficial</a><br><br>
For any questions, feel free to reach out to our Campus Caretaker, Bro. Ashish, on WhatsApp: <a href="https://wa.link/32bp71">Chat on WhatsApp</a><br><br>
Once again, welcome. We are glad God brought you to us.<br><br>
With love and blessings,<br>
TKT Online Campus<br>
(On behalf of Bishop Samuel Patta & Ps. Merlyn Patta)
</body>
</html>
"""

def send_welcome_emails(excel_path):
    with Image.open(IMAGE_PATH) as im:
        im.thumbnail((600, 600))
        im.save(RESIZED_PATH, format="JPEG")

    df = pd.read_excel(excel_path)
    yag = yagmail.SMTP(user=SENDER, password=PASSWORD)

    for _, row in df.iterrows():
        email = str(row["Email Address"]).strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print(f"Skipped invalid email: '{email}'")
            continue
        first_name = str(row["Name"]).strip().split()[0].capitalize()
        subject = SUBJECT_TEMPLATE.format(first_name=first_name)
        body = BODY_TEMPLATE.format(first_name=first_name)
        yag.send(to=email, subject=subject, contents=[yagmail.inline(RESIZED_PATH), body])
        print(f"Email sent to {email} ({first_name})")

if __name__ == "__main__":
    import sys
    excel = sys.argv[1] if len(sys.argv) > 1 else "newcomers_final.xlsx"
    send_welcome_emails(excel)
