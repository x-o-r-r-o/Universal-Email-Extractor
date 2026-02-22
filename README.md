# Universal Email & URL Extractor -- Complete & Detailed Documentation (All Versions)

## Overview

A robust suite of Python tools for extracting and filtering emails and
URLs from almost any file type. This documentation covers: - All
extractor scripts (simple, filtered, multi-threaded, advanced, and
Streamlit web version) - Features, requirements, installation, detailed
usage, and expected outputs - Per-script command-line and UI usage
examples - Blocklist/disposable logic - Troubleshooting, FAQ, and
contribution guidelines

## Features (All Versions)

-   **Recursive folder scan:** Processes all files in a directory tree
-   **Multi-format support:** Text, CSV, Excel, Word, PowerPoint, PDF,
    HTML, JSON, images (OCR), archives, databases, emails, and more
-   **Email/URL extraction from:**
    -   Text/config/code: `.txt`, `.csv`, `.log`, `.ini`, `.html`,
        `.json`, `.xml`, `.md`, etc.
    -   Office: `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`,
        `.rtf`, `.odt`, `.ods`, etc.
    -   PDFs (text-based and image-based with OCR)
    -   Images: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.gif`
        (Tesseract OCR)
    -   Databases: `.db`, `.sqlite`, `.sql`, `.mdb`, `.accdb`
    -   Email files: `.eml`, `.msg`
    -   Archives: `.zip`, `.tar`, `.gz`, `.rar`
-   **Real-time output:** Emails and URLs written as soon as found
-   **Deduplication:** No repeated emails or URLs
-   **Strict filtering:**
    -   Excludes emails with forbidden words (e.g., user, test, demo)
    -   Excludes emails from disposable/temporary providers
    -   Excludes URLs by blocklist (domain, extension, substring,
        wildcard)
-   **Progress bar & per-file logging**
-   **Summary report at completion**
-   **Handles edge cases:** Concatenated URLs, trailing junk, and more
-   **Fault-tolerant:** Logs errors, skips unreadable files, continues
-   **Easy to extend for new file types**

## Requirements

-   **Python 3.8+**
-   **Tesseract OCR** (for image/PDF OCR support)
-   **Python packages:** See `requirements.txt` (provided below)

## Installation

1.  **Clone the repository:**

-   git clone https://github.com/x-o-r-r-o/Universal-Email-Extractor/
        cd Universal-Email-Extractor

2.  **Install Python dependencies:**

-   pip install -r requirements.txt
        # For .doc/.ppt: pip install textract

3.  **Install Tesseract OCR:**

    -   Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
    -   Windows: Download from
        https://github.com/tesseract-ocr/tesseract/wiki (add to PATH)
    -   macOS: `brew install tesseract`

4.  **Prepare blocklists:**

    -   `disposable_domains.txt`: One disposable email domain per line
    -   `blocked_domains.txt`: One substring, domain, or extension per
        line (e.g., gov, .ru, \*.gov.pk)

## Blocklists & Filtering Logic

-   **Emails:** Filtered by forbidden words and disposable domains
-   **URLs:** Filtered by any substring, domain, or extension in
    `blocked_domains.txt` (wildcards, dots, and partial matches
    supported)
-   **Example blocklists:**
    -   `disposable_domains.txt`: `mailinator.com`, `tempmail.com`, ...
    -   `blocked_domains.txt`: `gov`, `.gov`, `gov.pk`, `.gov.pk`,
        `googleapis.com`, `.ru`, ...
-   **All entries are treated as substrings for blocking.**

## 1. Streamlit Web Dashboard Version

**Files:** `dashboard_pro.py` (+ `streamlit_extractor_backend.py`)

### Features

-   Full-featured, browser-based UI
-   Live progress, stats, logs, and results
-   Download emails/URLs as CSV
-   Start/stop extraction from UI
-   All advanced options: folders, blocklists, deduplication,
    validation, mapping, etc.

### Usage

1.  Install requirements:

-   pip install -r requirements.txt

2.  Run the dashboard:

-   streamlit run dashboard_pro.py

3.  Use the web UI to configure, run, and monitor extraction jobs
    (choose input/output folders, block/disposable lists, options, etc.)

### Expected Output

-   Downloadable CSVs for emails and URLs
-   Live logs and extraction status in browser

## 2. Multi-threaded Extractor

**File:** `email_extractor_multi-thread.py`

### Features

-   Multi-threaded/multiprocessing for speed on large datasets
-   Recursive scan, deduplication, block/disposable lists

### Usage Example

    python email_extractor_multi-thread.py /path/to/scan \
      -e emails.txt -u urls.txt -b blocked_domains.txt -d disposable_domains.txt

-   Use `-e` for email output, `-u` for URL output
-   Add filtering/blocklist arguments as needed

### Expected Output

-   `emails.txt`: Unique, filtered emails
-   `urls.txt`: Unique, filtered URLs

## 3. Simple Extractor

**File:** `email_extractor_simple.py`

### Features

-   Minimal, easy to read/modify
-   Processes `.txt` or similar files in a folder

### Usage Example

    python email_extractor_simple.py /path/to/scan > emails.txt

-   No advanced options; just specify the folder

### Expected Output

-   `emails.txt` (stdout): List of extracted emails

## 4. Extractor with Filtering

**File:** `email_extractor_with_filter.py`

### Features

-   Filters by blocklists, forbidden words, disposable domains
-   Deduplication

### Usage Example

    python email_extractor_with_filter.py /path/to/scan \
      -e emails.txt -u urls.txt -b blocked_domains.txt -d disposable_domains.txt

-   Use `-e` for email output, `-u` for URL output
-   Add filtering/blocklist arguments as needed

### Expected Output

-   `emails.txt`: Filtered, deduplicated emails
-   `urls.txt`: Filtered, deduplicated URLs

## 5. Advanced Extractor

**File:** `extractor.py`

### Features

-   Handles many file types (text, Office, PDF, images, archives,
    databases, emails)
-   Strict filtering, deduplication, block/disposable support
-   Progress bar and logging
-   Detailed summary report

### Usage Example

    python extractor.py /path/to/scan \
      -e emails.txt -u urls.txt -b blocked_domains.txt -d disposable_domains.txt \
      --url_mode root --include_ext .txt,.csv

See all options:

    python extractor.py --help

### Expected Output

-   `emails.txt`: High-quality, production-grade email extraction
-   `urls.txt`: Filtered, deduplicated URLs
-   `extractor.log`: Progress and errors

## Unified requirements.txt

    streamlit
    pandas
    tqdm
    tldextract
    idna
    requests
    pdfplumber
    pytesseract
    Pillow
    python-docx
    striprtf
    chardet
    openpyxl
    xlrd
    extract-msg
    pyodbc
    textract
    rarfile
    argparse

## Troubleshooting

-   **OCR errors:** Ensure Tesseract OCR is installed and in PATH
-   **Old Office files:** Install textract and system dependencies
-   **MDB/ACCDB files:** Install pyodbc/msaccessdb if needed
-   **Large folders:** Scripts are optimized for memory and real-time
    writing
-   **Extend support:** Add new handlers to process_file for more
    formats

## FAQ

-   **Can I block any domain extension or substring?**
    -   Yes, just add it to blocked_domains.txt (e.g., gov, .gov, xyz,
        .ru, .gov.pk, etc.)
-   **Does it work on Windows, Linux, Mac?**
    -   Yes, with Python 3.8+ and Tesseract OCR installed
-   **Can I use my own block/disposable lists?**
    -   Yes, just edit the respective files
-   **How does it handle concatenated URLs?**
    -   It splits and cleans them, so only valid URLs are exported
-   **What if a file type isn't supported?**
    -   Add a handler in the script and register it in process_file

## Contribution

-   Fork the repo, create a branch, and submit a pull request
-   Open issues for bugs or feature requests

## License

MIT License

## Acknowledgments

-   Tesseract OCR
-   pandas
-   pdfplumber
-   python-docx
-   extract-msg
-   tqdm
-   And all open-source contributors!

## Author

x-o-r-r-o

## Summary Table

  ---------------------------------------------------------------------------------------------------------------------------
  Script/Version                    Use Case         Command Example                   Main Features     Output Files/Results
  --------------------------------- ---------------- --------------------------------- ----------------- --------------------
  dashboard_pro.py (+backend)       Web UI,          streamlit run dashboard_pro.py    Live UI, all      Download/email/URL
                                    interactive                                        options, live     CSVs, logs
                                    extraction                                         logs, download    

  email_extractor_multi-thread.py   Fast, parallel   python                            Multi-threaded,   emails.txt, urls.txt
                                    extraction (CLI) email_extractor_multi-thread.py   blocklists,       
                                                     /path/to/scan                     deduplication     

  email_extractor_simple.py         Quick/simple     python email_extractor_simple.py  Basic, minimal,   emails.txt (stdout)
                                    extraction (CLI) /path/to/scan \> emails.txt       easy to modify    

  email_extractor_with_filter.py    Filtered         python                            Filtering,        emails.txt, urls.txt
                                    extraction (CLI) email_extractor_with_filter.py    deduplication     
                                                     /path/to/scan -e emails.txt -u                      
                                                     urls.txt                                            

  extractor.py                      Advanced,        python extractor.py /path/to/scan All features,     emails.txt,
                                    production       -e emails.txt -u urls.txt         reporting,        urls.txt, log
                                    extraction                                         logging           
  ---------------------------------------------------------------------------------------------------------------------------
