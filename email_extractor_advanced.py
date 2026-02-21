import os
import re
import csv
import json
import threading
import tempfile
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

import chardet
import pdfplumber
import pytesseract
from PIL import Image
import filetype
import openpyxl
import xlrd
import python_docx
import striprtf
import odf.opendocument
import odf.text
import extract_msg

CHECKPOINT_FILE = 'processed_files.json'

# --- Blocklist and Disposable Domains ---
def load_blocklist(filepath):
    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            entry = line.strip()
            if not entry or entry.startswith('#'):
                continue
            # Wildcards to regex
            entry_regex = re.escape(entry).replace(r'\*', '.*')
            patterns.append(re.compile(entry_regex, re.IGNORECASE))
    return patterns

def is_blocked(domain, block_patterns):
    return any(p.search(domain) for p in block_patterns)

def load_disposable_domains(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

# --- Email & URL Extraction ---
def extract_emails(text, forbidden_words, disposable_domains):
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    results = set()
    for email in email_regex.findall(text):
        local, _, domain = email.lower().partition('@')
        if any(word in local for word in forbidden_words):
            continue
        if any(domain.endswith(d) for d in disposable_domains):
            continue
        # Avoid filenames, numbers after @, etc.
        if re.search(r'@\d+$', email) or re.search(r'\.(jpg|png|gif|bmp|tiff|jpeg)$', email, re.I):
            continue
        results.add(email)
    return results

def extract_urls(text, block_patterns):
    url_regex = re.compile(r'https?://[^\s\'"<>]+')
    results = set()
    for url in url_regex.findall(text):
        try:
            domain = re.search(r'https?://([^/]+)', url).group(1).lower()
            if is_blocked(domain, block_patterns):
                continue
            # Remove trailing punctuation
            url = url.rstrip('.,;\'"!?)]}')
            # Split concatenated URLs
            for u in re.split(r'(https?://)', url):
                if u.startswith('http'):
                    results.add(u)
        except Exception:
            continue
    return results

# --- File Handlers ---
def read_text_file(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
            enc = chardet.detect(raw)['encoding'] or 'utf-8'
            return raw.decode(enc, errors='ignore')
    except Exception:
        return ''

def read_pdf_file(path):
    try:
        with pdfplumber.open(path) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)
    except Exception:
        return ''

def ocr_image(img_path):
    try:
        img = Image.open(img_path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ''

def read_image_file(path):
    return ocr_image(path)

def read_docx_file(path):
    try:
        doc = python_docx.Document(path)
        return '\n'.join([p.text for p in doc.paragraphs])
    except Exception:
        return ''

def read_rtf_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return striprtf.rtf_to_text(f.read())
    except Exception:
        return ''

# Add other handlers for xls, xlsx, pptx, odt, ods, eml, msg, db, etc.

def extract_archive(path, temp_dir):
    # Extract and return list of files inside archive
    extracted_files = []
    try:
        if path.lower().endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(path, 'r') as z:
                z.extractall(temp_dir)
                extracted_files.extend([os.path.join(temp_dir, f) for f in z.namelist()])
        # Add TAR, GZ, RAR extraction as needed
    except Exception:
        pass
    return extracted_files

def process_file(path, forbidden_words, disposable_domains, block_patterns, temp_dir):
    ext = os.path.splitext(path)[1].lower()
    text = ''
    extracted_files = []
    if ext in ('.txt', '.csv', '.log', '.ini', '.json', '.xml', '.html', '.htm', '.md', '.yaml', '.yml'):
        text = read_text_file(path)
    elif ext in ('.pdf',):
        text = read_pdf_file(path)
        # Also OCR for image-based PDFs (not shown here)
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'):
        text = read_image_file(path)
    elif ext in ('.docx',):
        text = read_docx_file(path)
    elif ext in ('.rtf',):
        text = read_rtf_file(path)
    elif ext in ('.zip', '.tar', '.gz', '.rar'):
        extracted_files = extract_archive(path, temp_dir)
    # Add more file handlers here as needed

    emails, urls = set(), set()
    if text:
        emails = extract_emails(text, forbidden_words, disposable_domains)
        urls = extract_urls(text, block_patterns)
    return emails, urls, extracted_files

def get_all_files(folder):
    for root, _, files in os.walk(folder):
        for f in files:
            yield os.path.join(root, f)

def save_checkpoint(processed):
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed), f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def main(folder, email_out, url_out, csv_out, blocklist_file, disposable_file, forbidden_words):
    block_patterns = load_blocklist(blocklist_file)
    disposable_domains = load_disposable_domains(disposable_file)

    processed_files = load_checkpoint()
    all_files = [f for f in get_all_files(folder) if f not in processed_files]
    all_emails, all_urls = set(), set()
    csv_rows = []

    lock = threading.Lock()
    temp_dir = tempfile.mkdtemp()
    try:
        with tqdm(total=len(all_files), desc="Scanning files", unit="file") as pbar, \
             ThreadPoolExecutor(max_workers=8) as executor, \
             open(email_out, 'a', encoding='utf-8') as ef, \
             open(url_out, 'a', encoding='utf-8') as uf:

            futures = {executor.submit(process_file, f, forbidden_words, disposable_domains, block_patterns, temp_dir): f for f in all_files}
            for future in as_completed(futures):
                f = futures[future]
                try:
                    emails, urls, extracted_files = future.result()
                    with lock:
                        for e in emails - all_emails:
                            ef.write(e + '\n')
                            csv_rows.append([e, f])
                        for u in urls - all_urls:
                            uf.write(u + '\n')
                            csv_rows.append([u, f])
                        all_emails.update(emails)
                        all_urls.update(urls)
                        processed_files.add(f)
                        save_checkpoint(processed_files)
                    # Enqueue extracted files from archives for processing
                    for efp in extracted_files:
                        all_files.append(efp)
                        pbar.total += 1
                except Exception as e:
                    print(f"[ERROR] {f}: {e}")
                finally:
                    pbar.update(1)

        if csv_out:
            with open(csv_out, 'w', newline='', encoding='utf-8') as cf:
                writer = csv.writer(cf)
                writer.writerow(['Value', 'Source File'])
                writer.writerows(csv_rows)

        print("\nSummary:")
        print(f"Total files processed: {len(processed_files)}")
        print(f"Unique emails found: {len(all_emails)}")
        print(f"Unique URLs found: {len(all_urls)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Universal Email & URL Extractor (Multithreaded, OCR, All Formats)")
    parser.add_argument('folder', help='Folder to scan')
    parser.add_argument('-o', '--output', default='emails_found.txt', help='Output file for emails')
    parser.add_argument('-u', '--url_output', default='urls_found.txt', help='Output file for URLs')
    parser.add_argument('-c', '--csv_output', default=None, help='CSV output file (optional)')
    parser.add_argument('-b', '--blocklist', default='blocked_domains.txt', help='Blocked domains file')
    parser.add_argument('-d', '--disposable', default='disposable_domains.txt', help='Disposable domains file')
    parser.add_argument('-f', '--forbidden', nargs='*', default=['user', 'test', 'demo', 'example', 'sample', 'dummy', 'temp', 'trial', 'no-reply', 'noreply'], help='Forbidden words in emails')
    args = parser.parse_args()

    main(args.folder, args.output, args.url_output, args.csv_output, args.blocklist, args.disposable, args.forbidden)
