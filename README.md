# Universal Email & URL Extractor

A production-ready Python tool for extracting and filtering emails and URLs from nearly any file type, with advanced filtering, real-time output, and robust reporting. This document provides complete usage and setup information for developers and technical users.

## Features

* Recursive folder scan (processes all files in a directory tree)
* Multi-format support: text, CSV, Excel, Word, PowerPoint, PDF, HTML, JSON, images (OCR), archives, databases, emails, and more
* Real-time output: emails and URLs are written to separate files as found
* Deduplication: no repeated emails or URLs
* Strict filtering:
  + Excludes emails with forbidden words (user, test, demo, etc.)
  + Excludes emails from disposable/temporary providers
  + Excludes URLs by domain, extension, substring, or wildcard (including partial matches, wildcards, and domain extensions)
* Progress bar and per-file logging
* Summary report at completion
* Handles concatenated URLs and ensures only clean URLs are exported
* Fault-tolerant: logs errors, skips unreadable files, and continues
* Easy to extend for new file types

## Requirements

* Python 3.8 or newer
* Tesseract OCR (for image/PDF OCR support)
* Python packages (see requirements.txt)

## Installation Steps

1. **Clone the repository**

* git clone <your-repo-url>
  cd Universal-Email-Extractor

1. **Install Python dependencies**

* pip install -r requirements.txt
* *(For .doc/.ppt support, also run: pip install textract)*

1. **Install Tesseract OCR**
   * **Ubuntu/Debian:**
   * sudo apt-get install tesseract-ocr
   * **Windows:** Download and install from: https://github.com/tesseract-ocr/tesseract/wiki Ensure tesseract is in your system PATH.
   * **macOS (Homebrew):**
   * brew install tesseract
2. **Prepare blocklists**
   * disposable\_domains.txt: one disposable email domain per line
   * blocked\_domains.txt: one substring, domain, or extension per line (e.g., gov, .ru, \*.gov.pk). All entries are treated as substrings for blocking. Wildcards, dots, and extensions are handled automatically.

## Usage

### Basic command

python extractor.py /path/to/scan

### Custom output and log files

python extractor.py /path/to/scan -o my\_emails.txt -u my\_urls.txt -l my\_logfile.log

### Custom disposable and blocked domains files

python extractor.py /path/to/scan -d my\_disposable\_domains.txt -b my\_blocked\_domains.txt

### Show help

python extractor.py --help

## Command-Line Arguments

| Flag/Argument | Description | Default |
| --- | --- | --- |
| folder | (positional) Folder to scan recursively | - |
| -o, --output | Output file for emails | emails\_found.txt |
| -u, --url\_output | Output file for URLs | urls\_found.txt |
| -l, --log | Log file | extractor.log |
| -d, --domains | Disposable email domains file | disposable\_domains.txt |
| -b, --blocked\_domains | Blocked URL domains/substrings/extensions file | blocked\_domains.txt |

## Filtering Logic

* **Emails**: filtered by forbidden words and disposable domains.
* **URLs**: filtered by any substring, domain, or extension listed in blocked\_domains.txt (e.g., gov, .ru, gov.pk blocks all such domains, including wildcards and partial matches).
* Blocklist entries can be plain, with dot, wildcard, or just a substring (all treated as substrings).

## Example Blocklists

**disposable\_domains.txt**

mailinator.com
tempmail.com
10minutemail.com
example.com

**blocked\_domains.txt**

gov
.gov
gov.pk
.gov.pk
googleapis.com
fonts.googleapis.com
xyz
.ru

*All of these will block any domain containing those substrings, including subdomains and domain extensions.*

## Output Files

* **Emails:** emails\_found.txt (or as specified)
* **URLs:** urls\_found.txt (or as specified)
* **Log:** extractor.log (or as specified)

## Main Functions (Defined in extractor.py)

* setup\_logger(logfile): Configures logging
* load\_disposable\_domains(filepath): Loads disposable email domains
* load\_blocked\_domains(filepath): Loads blocked URL substrings/extensions
* extract\_emails\_from\_text(text, disposable\_domains): Extracts and filters emails
* extract\_urls\_from\_text(text, blocked\_domains): Extracts, splits, and filters clean URLs (handles concatenated URLs and substring blocking)
* Format-specific file readers: (e.g., read\_text\_file, read\_csv\_file, read\_pdf\_file, etc.)
* process\_file(file\_path, temp\_dir, disposable\_domains): Detects file type, extracts emails and text
* scan\_folder(...): Main function to scan, extract, filter, deduplicate, log, and summarize

## Example Output

Total files found: 1234
Compatible files for extraction: 1022

--- Extraction Summary ---
Total unique emails found (before filtering): 400
Removed due to forbidden words: 12
Removed due to disposable domains: 25
Valid emails exported: 363 (see emails\_found.txt)
Total unique urls found: 150
Removed due to blocked domains: 24
Valid urls exported: 126 (see urls\_found.txt)
Files with emails/urls found: 332 / 1022

## Troubleshooting & Possibilities

* **OCR errors:** Ensure Tesseract OCR is installed and in PATH.
* **Old Office files:** Install textract and system dependencies.
* **MDB/ACCDB files:** Install pyodbc/msaccessdb if needed.
* **Large folders:** Script is optimized for memory and real-time writing.
* **Extend support:** Add new handlers to process\_file for more formats.

## FAQ

* **Can I block any domain extension or substring?** Yes, just add it to blocked\_domains.txt (e.g., gov, .gov, xyz, .ru, .gov.pk, etc.)
* **Does it work on Windows, Linux, Mac?** Yes, with Python 3.8+ and Tesseract OCR installed.
* **Can I use my own block/disposable lists?** Yes, just edit the respective files.
* **How does it handle concatenated URLs?** It splits and cleans them, so only valid URLs are exported.
* **What if a file type isn’t supported?** Add a handler in the script and register it in process\_file.

## License

MIT License (or your own)

## Credits

Developed by x-o-r-r-o.
