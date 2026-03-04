# TKT Online Campus — Weekly Sync Automation

> A fully automated weekly pipeline that extracts new member registrations, enriches them with AI, uploads to Google Sheets, generates contact files, and sends personalized welcome emails — all with a single command.

---

## Quick Start

```bash
./start.sh
```

That's it. The entire pipeline runs end to end.

---

## Pipeline Flow

```
┌─────────────────────────────────┐
│        ./start.sh               │
│   (single command entry point)  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  [1] weekly_sync.py             │
│                                 │
│  • Reads last email from        │
│    sync_tracker.db              │
│  • Finds it in TKT_EFAMILY_FORM │
│  • Extracts all records after   │
│  • Validates emails             │
│  • Cleans names                 │
│  • Enriches via OpenAI          │
│    (country, continent, phone)  │
│  • Uploads to EFAMILY MAIN      │
│    Sheet2 (Google Sheets)       │
│  • Updates DB with last email   │
└────────────────┬────────────────┘
                 │ newcomers.xlsx (overwritten)
                 ▼
┌─────────────────────────────────┐
│  [2] enrich_data.py             │
│                                 │
│  • Reads newcomers.xlsx         │
│  • Calls OpenAI GPT-4o-mini     │
│    per record for:              │
│    - Country                    │
│    - Continent                  │
│    - Corrected phone number     │
└────────────────┬────────────────┘
                 │ newcomers_enriched.xlsx (overwritten)
                 ▼
┌─────────────────────────────────┐
│  [3] clean_phones.py            │
│                                 │
│  • Reads newcomers_enriched     │
│  • Strips all non-digit chars   │
│    from phone numbers           │
└────────────────┬────────────────┘
                 │ newcomers_final.xlsx (overwritten)
                 ▼
┌─────────────────────────────────┐
│  [4] upload_to_sheets.py        │
│                                 │
│  • Uploads records to           │
│    EFAMILY MAIN Sheet2          │
│  • Updates sync_tracker.db      │
│    (replaces last email)        │
│                                 │
│  Calls vcard_converter.py ──────┼──► newcomers_phone.xlsx (overwritten)
│                                 │    newcomers.vcf (overwritten)
│                                 │
│  • Emails newcomers.vcf     ────┼──► efamcare@gmail.com
│  • Emails newcomers_final   ────┼──► avation2k14@gmail.com
│                                 │
│  Calls welcome_email.py ────────┼──► Welcome email → each new member
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  sync_tracker.db updated        │
│  Last email = newest member     │
└─────────────────────────────────┘
```

---

## File Reference

### Scripts

| File | Purpose |
|------|---------|
| `start.sh` | Entry point. Sets up venv, installs deps, runs full pipeline in order |
| `weekly_sync.py` | Core sync — reads DB, extracts new records from source sheet, enriches with OpenAI, uploads to destination sheet |
| `enrich_data.py` | Standalone enrichment — calls OpenAI to add country, continent, corrected phone |
| `clean_phones.py` | Strips all non-digit characters from phone numbers |
| `upload_to_sheets.py` | Uploads `newcomers_final.xlsx` to Google Sheets, triggers VCF generation and all email sending |
| `vcard_converter.py` | Extracts Name + Phone from `newcomers_final.xlsx`, creates `newcomers_phone.xlsx` and `newcomers.vcf` |
| `welcome_email.py` | Sends personalized HTML welcome email with church image to each new member |
| `send_africa_fellowship.py` | Standalone script to send Africa Fellowship invitation emails from an Excel file |

### Generated Files (Temporary — overwritten each run)

| File | Created by | Contents |
|------|-----------|---------|
| `newcomers.xlsx` | `weekly_sync.py` | Raw new records from source form |
| `newcomers_enriched.xlsx` | `enrich_data.py` | Records with country, continent, corrected phone |
| `newcomers_final.xlsx` | `clean_phones.py` | Final cleaned records ready for upload |
| `newcomers_phone.xlsx` | `vcard_converter.py` | Name + Phone only |
| `newcomers.vcf` | `vcard_converter.py` | vCard contact file of all new members |

> ⚠️ These files only ever contain the **current week's batch**. They are fully overwritten on every run — old data is gone.

### Persistent Files

| File | Purpose |
|------|---------|
| `sync_tracker.db` | SQLite database — stores the last synced email. Single source of truth for incremental sync. Replaces the record on every run (never accumulates) |
| `credentials.json` | Google Service Account key — required for Sheets API access |
| `.env` | Contains `OPENAI_API_KEY` |

---

## Google Sheets

| Sheet | Role |
|-------|------|
| `TKT_EFAMILY _FORM` | Source — member registration form responses |
| `EFAMILY MAIN_20-10-25` → Sheet2 | Destination — master member database |

---

## State Management

The pipeline uses `sync_tracker.db` as the single source of truth:

- On every run, `weekly_sync.py` reads the **last synced email** from the DB
- It finds that email in the source form and processes everything **after** it
- After a successful upload, the DB is updated — old email deleted, new last email saved
- This guarantees no duplicates and no missed records regardless of what's in the Google Sheet

---

## Email Outputs

| Recipient | What they receive |
|-----------|------------------|
| Each new member | Personalized HTML welcome email with church image |
| `efamcare@gmail.com` | `newcomers.vcf` — contact file of all new members |
| `avation2k14@gmail.com` | `newcomers_final.xlsx` — full new members list |

---

## Prerequisites

- Python 3.8+
- `credentials.json` — Google Service Account with access to both sheets
- `.env` file with `OPENAI_API_KEY`
- Both Google Sheets shared with the service account email (Editor access)

---

## Dependencies

```
gspread
google-auth
openai
pandas
openpyxl
yagmail
Pillow
python-dotenv
```

Installed automatically by `start.sh`.

---

## Troubleshooting

**No new records found**
The DB last email matches the last entry in the source form — nothing new to process. This is expected.

**OpenAI enrichment fails for a record**
The record is still saved with `country: Unknown`, `continent: Unknown`. The pipeline does not stop.

**Duplicate entries in Google Sheet**
Do not use the destination sheet as the source of truth. The DB (`sync_tracker.db`) is always authoritative. Check the last email with:
```bash
sqlite3 sync_tracker.db "SELECT last_email, sync_date FROM last_sync;"
```

---

*Built for TKT Online Campus — automated with love.*
