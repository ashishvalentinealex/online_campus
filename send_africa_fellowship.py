import re
import yagmail
import pandas as pd
from PIL import Image

# --- Config ---
EXCEL_PATH  = "/home/user/Downloads/TKT_AFRICA.xlsx"
IMAGE_PATH  = "/home/user/Downloads/tktfamily.jpeg"
SENDER     = "efamcare@gmail.com"
PASSWORD   = "evkzzjrlkbepxqsm"

SUBJECT_TEMPLATE = "{first_name}, Africa Is Calling – Join Our Weekly Faith Fellowship"

# Resize image to temp file
RESIZED_PATH = "/tmp/TKT_CHURCH.jpeg"
with Image.open(IMAGE_PATH) as im:
    im.thumbnail((600, 600))
    im.save(RESIZED_PATH, format="JPEG")

BODY_TEMPLATE = """
<html>
<body style="font-family:Arial,sans-serif;font-size:15px;color:#222;line-height:1.5;margin:0;padding:16px;">
Dear {first_name},<br>
Greetings from the Online Campus of TKT Church, on behalf of Bishop Samuel Patta and Ps. Merlyn Patta.<br>
We are launching a weekly <strong>Africa Online Fellowship</strong> scheduled in African time zones, so you can grow in faith, prayer, and the Word without time barriers.<br>
If you would like to join us, please register below:<br>
<strong><a href="https://forms.gle/bZHoGjNGdBkjfFm28">Click Here to Register</a></strong><br>
For any questions, you may contact us on WhatsApp:<br>
Sis. Deepshika – +91 91006 85544 (<a href="https://wa.link/8duwnq">Chat on WhatsApp</a>)<br>
Sis. Sharon – +91 99729 87730 (<a href="https://wa.link/kyoo0s">Chat on WhatsApp</a>)<br>
Bro. Ashish – +91 87905 88431 (<a href="https://wa.link/4suhtc">Chat on WhatsApp</a>)<br><br>
All meetings are held on <strong>Zoom and are completely free.</strong>
To know more about us, visit our YouTube channel:<br>
<a href="https://www.youtube.com/@tktchurchofficial">https://www.youtube.com/@tktchurchofficial</a><br>
We look forward to welcoming you.<br>
Blessings,
TKT Online Campus
(On behalf of Bishop Samuel Patta & Ps. Merlyn Patta)
</body>
</html>
"""

# --- Load recipients ---
# Excel should have at minimum an 'Email' and 'Name' column
df = pd.read_excel(EXCEL_PATH)

# --- Send emails ---
yag = yagmail.SMTP(user=SENDER, password=PASSWORD)

for _, row in df.iterrows():
    email = str(row["Email"]).strip()
    if not re.fullmatch(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", email):
        print(f"Skipped invalid email: '{email}'")
        continue
    first_name = str(row["Name"]).strip().split()[0].capitalize()
    subject = SUBJECT_TEMPLATE.format(first_name=first_name)
    body = BODY_TEMPLATE.format(first_name=first_name)
    yag.send(to=email, subject=subject, contents=[yagmail.inline(RESIZED_PATH), body])
    print(f"Email sent to {email} ({first_name})")
