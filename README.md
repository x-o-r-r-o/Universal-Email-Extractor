# Universal Email Extractor

A **production-ready, robust Python program** to extract valid email
addresses from nearly any file or folder.

Supports text, Office documents (old & new), PDFs, images (with OCR),
databases, emails, archives, and more. **Real-time output:** Emails are
written to the output file as soon as they are found.

## Features

-   **Scans folders recursively** for all supported file types
-   **Extracts emails from:**
    -   Text/config/code files: `.txt`, `.csv`, `.log`, `.ini`, `.inf`,
        `.html`, `.htm`, `.asp`, `.aspx`, `.php`, `.js`, `.json`,
        `.xml`, `.yaml`, `.yml`, `.md`, etc.
    -   Office documents: `.doc`, `.docx`, `.docm`, `.xls`, `.xlsx`,
        `.xlsm`, `.ppt`, `.pptx`, `.rtf`, `.odt`, `.ods`, etc.
    -   PDFs (text-based and image-based with OCR)
    -   Images: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.gif`, etc.
        (using Tesseract OCR)
    -   Databases: `.db`, `.sqlite`, `.sqlite3`, `.sql`, `.mdb`,
        `.accdb`
    -   Email files: `.eml`, `.msg`
    -   Archives: `.zip`, `.tar`, `.gz`, `.rar` (recursive extraction)
-   **Strict filtering:** Avoids false positives from filenames and fake
    emails
-   **Progress bar** and live per-file logging
-   **Writes emails immediately** to output file
-   **Deduplicates** emails automatically
-   **Robust error handling** and logging
-   **Easy to extend** for new file types

## Requirements

-   **Python 3.7+**
-   **Tesseract OCR** (for image and image-based PDF extraction)
-   Python packages (see below)

## Installation

### 1. Clone the repository

    git clone https://github.com/x-o-r-r-o/Universal-Email-Extractor.git
    cd Universal-Email-Extractor

### 2. Install Tesseract OCR

-   **Windows:** Download and install from [Tesseract at UB
    Mannheim](https://github.com/tesseract-ocr/tesseract/wiki)
-   **Linux:** `sudo apt-get install tesseract-ocr`
-   **macOS (Homebrew):** `brew install tesseract`

### 3. Install Python dependencies

    pip install -r requirements.txt

`requirements.txt`**:**

    pdfplumber
    pytesseract
    pillow
    python-docx
    openpyxl
    xlrd
    pandas
    striprtf
    odfpy
    extract-msg
    chardet
    filetype
    tqdm

## Usage

### Basic Command

    python email_extractor.py <folder_to_scan>

### Common Options

  -----------------------------------------------------------------------------
  Option           Description                             Default
  ---------------- --------------------------------------- --------------------
  `-o, --output`   Output file for found emails            `emails_found.txt`

  `-l, --log`      Log file for progress/errors            `extractor.log`
  -----------------------------------------------------------------------------

**Example:**

    python email_extractor.py ./data -o results.txt -l run.log

## How It Works

-   **Recursively scans** the given folder for all supported file types.
-   **Extracts text** using the best available method for each file
    type.
-   **Extracts emails** with strict filtering to avoid false positives:
    -   Only real, valid email addresses (not filenames or image names)
    -   Ignores emails ending in file extensions or with numbers after
        `@`
-   **Writes new emails immediately** to output file (no waiting for the
    scan to finish).
-   **Shows a progress bar** and per-file status in the terminal.
-   **Logs all actions and errors** to the log file.

## Supported File Types

-   **Text/Config:** `.txt`, `.log`, `.ini`, `.inf`, `.html`, `.htm`,
    `.asp`, `.aspx`, `.php`, `.js`, `.json`, `.xml`, `.yaml`, `.yml`,
    `.md`
-   **Spreadsheets:** `.csv`, `.xls`, `.xlsx`, `.xlsm`, `.ods`
-   **Documents:** `.doc`, `.docx`, `.docm`, `.rtf`, `.odt`
-   **Presentations:** `.ppt`, `.pptx`
-   **PDFs:** `.pdf`
-   **Images:** `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.gif`
-   **Databases:** `.sqlite`, `.sqlite3`, `.db`, `.sql`, `.mdb`,
    `.accdb`
-   **Emails:** `.eml`, `.msg`
-   **Archives:** `.zip`, `.tar`, `.gz`, `.rar` (recursive extraction)

## Example Output

**Progress bar and console output:**

    Total files found: 152
    Compatible files for extraction: 47
    Extracting emails:  65%|███████████████▌        | 31/47 [00:04<00:02,  6.90it/s]
    Processing file 32/47: ./data/contacts.xlsx
      Found emails in ./data/contacts.xlsx: {'john.doe@email.com', 'info@company.org'}
    Processing file 33/47: ./data/invoice.pdf
      Found emails in ./data/invoice.pdf: {'billing@vendor.com'}
    ...
    Extraction complete. Unique emails found: 24. See results.txt.
    Files with emails found: 17 / 47

**Sample** `emails_found.txt` **output:**

    john.doe@email.com
    info@company.org
    billing@vendor.com
    support@website.net
    ...

## Screenshots

### Terminal Progress Example

  -----------------------------------------------------------------------
  Progress bar and per-file output

  -----------------------------------------------------------------------

Progress bar and per-file output

### Example Output File

  -----------------------------------------------------------------------
  Emails found output

  -----------------------------------------------------------------------

Emails found output

## FAQ

### Q: Why do I need Tesseract OCR?

**A:** Tesseract is required to extract emails from images and
image-based PDFs. Without it, the program will skip those files.

### Q: How do I add support for more file types?

**A:** Add a new handler function in the script and register its
extension in the `process_file` function.

### Q: The script is slow on large archives or files. How can I speed it up?

**A:** For huge datasets, consider splitting the folder, running in
parallel, or excluding archive extraction if not needed.

### Q: I see no emails in the output, but I know there are some.

**A:** Check the log file for errors, make sure the files are supported,
and that Tesseract is installed for image extraction.

### Q: Can I run this on Windows/Mac/Linux?

**A:** Yes! It works cross-platform, but Tesseract must be installed and
accessible in your system path.

### Q: Where can I report bugs or contribute?

**A:** Open an issue or pull request on GitHub ([see Contributing
section](#contribution)).

## Troubleshooting

-   **Nothing is extracted:**
    -   Check that the folder contains supported file types.
    -   Look at the log file for errors.
    -   Make sure Tesseract OCR is installed and accessible.
-   **Filenames or fake emails are extracted:**
    -   The script uses strict filtering, but if you spot a false
        positive, please [open an issue](#contribution).
-   **Some file types not supported:**
    -   Extend the `process_file` function with new handlers.
-   **Permission errors:**
    -   Run as administrator or ensure you have read/write access to the
        target folders.

## Contribution

Contributions are welcome! - Fork the repo, create a branch, and submit
a pull request. - Open issues for bugs or feature requests.

## License

MIT License

## Acknowledgments

-   [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
-   [pandas](https://pandas.pydata.org/)
-   [pdfplumber](https://github.com/jsvine/pdfplumber)
-   [python-docx](https://python-docx.readthedocs.io/)
-   [extract-msg](https://github.com/mattgwwalker/msg-extractor)
-   [tqdm](https://github.com/tqdm/tqdm)
-   And all open-source contributors!

## Author

x-o-r-r-o
