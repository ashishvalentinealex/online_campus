# 🌍 Online Campus Weekly Sync Automation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Automated data synchronization pipeline for TKT Online Campus member management, featuring intelligent data validation, AI-powered enrichment, and seamless Google Sheets integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Workflow](#workflow)
- [Project Structure](#project-structure)
- [API Usage & Costs](#api-usage--costs)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Online Campus Weekly Sync Automation is a production-ready Python application designed to streamline the process of synchronizing member data between Google Sheets. It automatically extracts new member registrations, validates and enriches the data using AI, and uploads the processed records to the main database.

### Key Capabilities

- **Incremental Sync**: Only processes new records since the last sync
- **Data Validation**: Validates email addresses and filters invalid entries
- **AI-Powered Enrichment**: Uses OpenAI GPT-4o-mini to determine country, continent, and validate phone numbers
- **Name Normalization**: Removes titles and initials, standardizes naming conventions
- **Phone Number Standardization**: Cleans and formats international phone numbers
- **Persistent State**: Tracks last processed record using SQLite
- **Error Handling**: Robust error handling with detailed logging

## ✨ Features

### 🔍 Data Validation
- Email format validation with regex patterns
- Automatic filtering of invalid entries
- Whitespace trimming and normalization

### 🤖 AI-Powered Enrichment
- Geographic data enrichment (country and continent)
- Phone number validation and country code correction
- Intelligent data inference using OpenAI GPT-4o-mini

### 📊 Data Processing
- Name cleaning (removes Dr., Mr., Mrs., single-letter initials)
- Phone number standardization (removes spaces, hyphens, plus signs)
- Automatic appending of "TKT ONLINE CAMPUS" suffix to names

### 🔄 Automation
- One-command execution via shell script
- Automatic virtual environment setup
- Dependency management
- State persistence for incremental syncs

## 🏗️ Architecture

```
┌─────────────────────┐
│  TKT_EFAMILY_FORM   │  (Source)
│   Google Sheet      │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  Extract New │
    │   Records    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Validate   │
    │    Emails    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Clean Names │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  OpenAI API  │
    │  Enrichment  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Clean Phones │
    └──────┬───────┘
           │
           ▼
┌──────────────────────┐
│ EFAMILY MAIN Sheet2  │  (Destination)
│    Google Sheet      │
└──────────────────────┘
           │
           ▼
    ┌──────────────┐
    │  SQLite DB   │
    │ (Last Email) │
    └──────────────┘
```

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **Google Cloud Project**: With Sheets API and Drive API enabled
- **OpenAI API Key**: For data enrichment
- **Google Service Account**: With access to your Google Sheets

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/online-campus-sync.git
cd online-campus-sync
```

### 2. Set Up Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API
4. Create a Service Account:
   - Navigate to **APIs & Services > Credentials**
   - Click **Create Credentials > Service Account**
   - Download the JSON key file
5. Rename the file to `credentials.json` and place it in the project root

### 3. Share Google Sheets with Service Account

Share both Google Sheets with the service account email (found in `credentials.json`):
- `TKT_EFAMILY _FORM` (source sheet)
- `EFAMILY MAIN_20-10-25` (destination sheet)

Grant **Editor** permissions to the service account.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### 5. Run the Setup Script

```bash
./start.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Run the sync automation

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Google Sheets Configuration

Update the sheet names in `weekly_sync.py` if needed:

```python
SOURCE_SHEET = "TKT_EFAMILY _FORM"
DEST_SHEET = "EFAMILY MAIN_20-10-25"
```

## 💻 Usage

### Quick Start

```bash
./start.sh
```

### Manual Execution

```bash
# Activate virtual environment
source onlinecampus/bin/activate

# Run the sync
python weekly_sync.py
```

### First Run

On the first run, the script will:
1. Read the last email from the destination sheet
2. Find that email in the source sheet
3. Process all records after that email
4. Store the last processed email for future syncs

### Subsequent Runs

On subsequent runs, the script will:
1. Load the last processed email from the database
2. Only process new records since the last sync
3. Update the database with the new last email

## 🔄 Workflow

### Step-by-Step Process

1. **Connect to Google Sheets**
   - Authenticates using service account credentials
   - Opens source and destination sheets

2. **Identify New Records**
   - Retrieves last processed email from destination sheet
   - Finds that email in source sheet
   - Extracts all records after that position

3. **Validate Emails**
   - Checks email format using regex
   - Filters out invalid entries
   - Trims whitespace

4. **Clean Names**
   - Removes titles (Dr., Mr., Mrs., etc.)
   - Removes single-letter initials
   - Appends "TKT ONLINE CAMPUS" suffix

5. **Enrich with AI**
   - Sends city and phone to OpenAI API
   - Receives country, continent, and corrected phone number
   - Handles API errors gracefully

6. **Standardize Phone Numbers**
   - Removes all non-digit characters
   - Keeps only country code and number

7. **Upload to Destination**
   - Appends processed records to destination sheet
   - Stores last email in SQLite database

8. **Report Results**
   - Displays processing statistics
   - Shows token usage and estimated cost

## 📁 Project Structure

```
online-campus-sync/
├── weekly_sync.py          # Main automation script
├── start.sh                # Setup and execution script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore rules
├── credentials.json        # Google service account (not in git)
├── sync_tracker.db         # SQLite database (auto-generated)
├── README.md              # This file
└── onlinecampus/          # Virtual environment (auto-generated)
```

## 💰 API Usage & Costs

### OpenAI API (GPT-4o-mini)

**Pricing** (as of 2024):
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Estimated Cost per Record**:
- ~200-300 tokens per record
- ~$0.0001-0.0002 per record

**Example**:
- 100 records ≈ $0.01-0.02
- 1,000 records ≈ $0.10-0.20

### Google Sheets API

- **Free tier**: 60 requests per minute per user
- **Cost**: Free for typical usage

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Error

```
Error: APIError: [403]: Request had insufficient authentication scopes.
```

**Solution**: Ensure you've shared both Google Sheets with the service account email.

#### 2. OpenAI API Error

```
Error: OPENAI_API_KEY not found in .env file
```

**Solution**: Create a `.env` file with your OpenAI API key.

#### 3. No New Records

```
✅ No new records to sync!
```

**Solution**: This is normal if there are no new entries since the last sync.

#### 4. Invalid Email Format

The script automatically filters invalid emails and reports them:

```
Skipped invalid email: 'Ne'
```

**Solution**: No action needed. Invalid entries are automatically excluded.

### Debug Mode

To enable verbose logging, modify `weekly_sync.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Update README for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [gspread](https://github.com/burnash/gspread) - Google Sheets Python API
- [OpenAI](https://openai.com) - AI-powered data enrichment
- [openpyxl](https://openpyxl.readthedocs.io) - Excel file handling

## 📞 Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Contact the maintainers
- Check the [Troubleshooting](#troubleshooting) section

---

**Made with ❤️ for TKT Online Campus**

*Last updated: January 2026*
