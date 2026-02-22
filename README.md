# <a name="xcc06e43e393e5990b6ab7caeac76f94a0a095c1"></a>Universal Email & URL Extractor – Complete & Detailed Documentation (All Versions)
## <a name="overview"></a>Overview
A robust suite of Python tools for extracting and filtering emails and URLs from almost any file type. This documentation covers: - All extractor scripts (simple, filtered, multi-threaded, advanced, and Streamlit web version) - Features, requirements, installation, detailed usage, and expected outputs - Per-script command-line and UI usage examples - Blocklist/disposable logic - Troubleshooting, FAQ, and contribution guidelines

-----
## <a name="features-all-versions"></a>Features (All Versions)
- **Recursive folder scan:** Processes all files in a directory tree
- **Multi-format support:** Text, CSV, Excel, Word, PowerPoint, PDF, HTML, JSON, images (OCR), archives, databases, emails, and more
- **Email/URL extraction from:**
  - Text/config/code: .txt, .csv, .log, .ini, .html, .json, .xml, .md, etc.
  - Office: .doc, .docx, .xls, .xlsx, .ppt, .pptx, .rtf, .odt, .ods, etc.
  - PDFs (text-based and image-based with OCR)
  - Images: .jpg, .jpeg, .png, .bmp, .tiff, .gif (Tesseract OCR)
  - Databases: .db, .sqlite, .sql, .mdb, .accdb
  - Email files: .eml, .msg
  - Archives: .zip, .tar, .gz, .rar
- **Real-time output:** Emails and URLs written as soon as found
- **Deduplication:** No repeated emails or URLs
- **Strict filtering:**
  - Excludes emails with forbidden words (e.g., user, test, demo)
  - Excludes emails from disposable/temporary providers
  - Excludes URLs by blocklist (domain, extension, substring, wildcard)
- **Progress bar & per-file logging**
- **Summary report at completion**
- **Handles edge cases:** Concatenated URLs, trailing junk, and more
- **Fault-tolerant:** Logs errors, skips unreadable files, continues
- **Easy to extend for new file types**
-----
## <a name="requirements"></a>Requirements
- **Python 3.8+**
- **Tesseract OCR** (for image/PDF OCR support)
- **Python packages:** See requirements.txt (provided below)
-----
## <a name="installation"></a>Installation
1. **Clone the repository:**

   git clone https://github.com/x-o-r-r-o/Universal-Email-Extractor/\
   cd Universal-Email-Extractor
1. **Install Python dependencies:**

   pip install -r requirements.txt\
   *# For .doc/.ppt: pip install textract*
1. **Install Tesseract OCR:**
   - Ubuntu/Debian: sudo apt-get install tesseract-ocr
   - Windows: Download from https://github.com/tesseract-ocr/tesseract/wiki (add to PATH)
   - macOS: brew install tesseract
1. **Prepare blocklists:**
   - disposable\_domains.txt: One disposable email domain per line
   - blocked\_domains.txt: One substring, domain, or extension per line (e.g., gov, .ru, \*.gov.pk)
-----
## <a name="blocklists-filtering-logic"></a>Blocklists & Filtering Logic
- **Emails:** Filtered by forbidden words and disposable domains
- **URLs:** Filtered by any substring, domain, or extension in blocked\_domains.txt (wildcards, dots, and partial matches supported)
- **Example blocklists:**
  - disposable\_domains.txt: mailinator.com, tempmail.com, …
  - blocked\_domains.txt: gov, .gov, gov.pk, .gov.pk, googleapis.com, .ru, …
- **All entries are treated as substrings for blocking.**
-----
## <a name="streamlit-web-dashboard-version"></a>1. Streamlit Web Dashboard Version
**Files:** dashboard\_pro.py (+ streamlit\_extractor\_backend.py)
### <a name="features"></a>Features
- Full-featured, browser-based UI
- Live progress, stats, logs, and results
- Download emails/URLs as CSV
- Start/stop extraction from UI
- All advanced options: folders, blocklists, deduplication, validation, mapping, etc.
### <a name="usage"></a>Usage
1. Install requirements:

   pip install -r requirements.txt
1. Run the dashboard:

   streamlit run dashboard\_pro.py
1. Use the web UI to configure, run, and monitor extraction jobs (choose input/output folders, block/disposable lists, options, etc.)
### <a name="expected-output"></a>Expected Output
- Downloadable CSVs for emails and URLs
- Live logs and extraction status in browser
-----
## <a name="multi-threaded-extractor"></a>2. Multi-threaded Extractor
**File:** email\_extractor\_multi-thread.py
### <a name="features-1"></a>Features
- Multi-threaded/multiprocessing for speed on large datasets
- Recursive scan, deduplication, block/disposable lists
### <a name="usage-example"></a>Usage Example
python email\_extractor\_multi-thread.py /path/to/scan \\
`  `-e emails.txt -u urls.txt -b blocked\_domains.txt -d disposable\_domains.txt

- Use -e for email output, -u for URL output
- Add filtering/blocklist arguments as needed
### <a name="expected-output-1"></a>Expected Output
- emails.txt: Unique, filtered emails
- urls.txt: Unique, filtered URLs
-----
## <a name="simple-extractor"></a>3. Simple Extractor
**File:** email\_extractor\_simple.py
### <a name="features-2"></a>Features
- Minimal, easy to read/modify
- Processes .txt or similar files in a folder
### <a name="usage-example-1"></a>Usage Example
python email\_extractor\_simple.py /path/to/scan > emails.txt

- No advanced options; just specify the folder
### <a name="expected-output-2"></a>Expected Output
- emails.txt (stdout): List of extracted emails
-----
## <a name="extractor-with-filtering"></a>4. Extractor with Filtering
**File:** email\_extractor\_with\_filter.py
### <a name="features-3"></a>Features
- Filters by blocklists, forbidden words, disposable domains
- Deduplication
### <a name="usage-example-2"></a>Usage Example
python email\_extractor\_with\_filter.py /path/to/scan \\
`  `-e emails.txt -u urls.txt -b blocked\_domains.txt -d disposable\_domains.txt

- Use -e for email output, -u for URL output
- Add filtering/blocklist arguments as needed
### <a name="expected-output-3"></a>Expected Output
- emails.txt: Filtered, deduplicated emails
- urls.txt: Filtered, deduplicated URLs
-----
## <a name="advanced-extractor"></a>5. Advanced Extractor
**File:** extractor.py
### <a name="features-4"></a>Features
- Handles many file types (text, Office, PDF, images, archives, databases, emails)
- Strict filtering, deduplication, block/disposable support
- Progress bar and logging
- Detailed summary report
### <a name="usage-example-3"></a>Usage Example
python extractor.py /path/to/scan \\
`  `-e emails.txt -u urls.txt -b blocked\_domains.txt -d disposable\_domains.txt \\
`  `--url\_mode root --include\_ext .txt,.csv

See all options:

python extractor.py --help
### <a name="expected-output-4"></a>Expected Output
- emails.txt: High-quality, production-grade email extraction
- urls.txt: Filtered, deduplicated URLs
- extractor.log: Progress and errors
-----
## <a name="unified-requirements.txt"></a>Unified requirements.txt
pandas\
xlrd\
openpyxl\
python-docx\
pdfplumber\
pytesseract\
Pillow\
filetype\
chardet\
striprtf\
odfpy\
extract_msg\
tqdm\
python-pptx\
textract\
pyodbc\
msaccessdb\
tldextract\
streamlit\
idna\
requests\
extract-msg\
rarfile\
argparse

-----
## <a name="troubleshooting"></a>Troubleshooting
- **OCR errors:** Ensure Tesseract OCR is installed and in PATH
- **Old Office files:** Install textract and system dependencies
- **MDB/ACCDB files:** Install pyodbc/msaccessdb if needed
- **Large folders:** Scripts are optimized for memory and real-time writing
- **Extend support:** Add new handlers to process\_file for more formats
-----
## <a name="faq"></a>FAQ
- **Can I block any domain extension or substring?**
  - Yes, just add it to blocked\_domains.txt (e.g., gov, .gov, xyz, .ru, .gov.pk, etc.)
- **Does it work on Windows, Linux, Mac?**
  - Yes, with Python 3.8+ and Tesseract OCR installed
- **Can I use my own block/disposable lists?**
  - Yes, just edit the respective files
- **How does it handle concatenated URLs?**
  - It splits and cleans them, so only valid URLs are exported
- **What if a file type isn’t supported?**
  - Add a handler in the script and register it in process\_file
-----
## <a name="contribution"></a>Contribution
- Fork the repo, create a branch, and submit a pull request
- Open issues for bugs or feature requests
-----
## <a name="license"></a>License
MIT License

-----
## <a name="acknowledgments"></a>Acknowledgments
- Tesseract OCR
- pandas
- pdfplumber
- python-docx
- extract-msg
- tqdm
- And all open-source contributors!
-----
## <a name="author"></a>Author
x-o-r-r-o

-----
## <a name="summary-table"></a>Summary Table

|Script/Version|Use Case|Command Example|Main Features|Output Files/Results|
| :- | :- | :- | :- | :- |
|dashboard\_pro.py (+backend)|Web UI, interactive extraction|streamlit run dashboard\_pro.py|Live UI, all options, live logs, download|Download/email/URL CSVs, logs|
|email\_extractor\_multi-thread.py|Fast, parallel extraction (CLI)|python email\_extractor\_multi-thread.py /path/to/scan|Multi-threaded, blocklists, deduplication|emails.txt, urls.txt|
|email\_extractor\_simple.py|Quick/simple extraction (CLI)|python email\_extractor\_simple.py /path/to/scan > emails.txt|Basic, minimal, easy to modify|emails.txt (stdout)|
|email\_extractor\_with\_filter.py|Filtered extraction (CLI)|python email\_extractor\_with\_filter.py /path/to/scan -e emails.txt -u urls.txt|Filtering, deduplication|emails.txt, urls.txt|
|extractor.py|Advanced, production extraction|python extractor.py /path/to/scan -e emails.txt -u urls.txt|All features, reporting, logging|emails.txt, urls.txt, log|

