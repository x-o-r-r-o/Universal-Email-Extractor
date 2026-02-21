import os
import re
import csv
import json
import tempfile
import shutil
import multiprocessing
import threading
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import chardet
import pdfplumber
import pytesseract
from PIL import Image
import docx
import striprtf

CHECKPOINT_FILE = 'processed_files.json'

def load_blocklist(filepath):
    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            entry = line.strip()
            if not entry or entry.startswith('#'):
                continue
            entry_regex = re.escape(entry).replace(r'\*', '.*')
            patterns.append(re.compile(entry_regex, re.IGNORECASE))
    return patterns

def is_blocked(domain, block_patterns):
    return any(p.search(domain) for p in block_patterns)

def load_disposable_domains(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

def extract_emails(text, forbidden_words, disposable_domains):
    email_regex = re.compile(r'(?<![\w.-])([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(?![\w.-])')
    results = set()
    for email in email_regex.findall(text):
        local, _, domain = email.lower().partition('@')
        if any(word in local for word in forbidden_words):
            continue
        if any(domain.endswith(d) for d in disposable_domains):
            continue
        if re.search(r'@\d+$', email) or re.search(r'\.(jpg|png|gif|bmp|tiff|jpeg)$', email, re.I):
            continue
        results.add(email)
    return results

def extract_urls(text, block_patterns):
    url_candidates = []
    for match in re.finditer(r'https?://', text):
        start = match.start()
        end = start
        while end < len(text) and text[end] not in ' \'",\n\r\t<>[](){},;|':
            end += 1
        url = text[start:end]
        url = url.rstrip('.,;\'"!?)]}')
        if len(url) < 10 or '.' not in url:
            continue
        try:
            domain = re.search(r'https?://([^/]+)', url).group(1).lower()
            if is_blocked(domain, block_patterns):
                continue
        except Exception:
            continue
        url_candidates.append(url)
    return set(url_candidates)

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
        doc = docx.Document(path)
        return '\n'.join([p.text for p in doc.paragraphs])
    except Exception:
        return ''

def read_rtf_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return striprtf.rtf_to_text(f.read())
    except Exception:
        return ''

def extract_archive(path, temp_dir):
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
    return emails, urls, extracted_files, path

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

def writer(queue, email_out, url_out, csv_out):
    seen_emails = set()
    seen_domains = set()
    with open(email_out, 'a', encoding='utf-8') as ef, \
         open(url_out, 'a', encoding='utf-8') as uf, \
         (open(csv_out, 'a', encoding='utf-8', newline='') if csv_out else open(os.devnull, 'w')) as cf:
        csv_writer = csv.writer(cf) if csv_out else None
        while True:
            item = queue.get()
            if item == 'DONE':
                break
            emails, urls, src_file = item
            for e in emails:
                if e in seen_emails:
                    continue
                seen_emails.add(e)
                ef.write(e + '\n')
                if csv_writer:
                    csv_writer.writerow([e, src_file])
            for u in urls:
                try:
                    domain = re.search(r'https?://([^/]+)', u).group(1).lower()
                except Exception:
                    continue
                if domain in seen_domains:
                    continue
                seen_domains.add(domain)
                uf.write(u + '\n')
                if csv_writer:
                    csv_writer.writerow([u, src_file])
            ef.flush()
            uf.flush()
            if csv_writer:
                cf.flush()

def main(folder, email_out, url_out, csv_out, blocklist_file, disposable_file, forbidden_words, num_processes=4):
    block_patterns = load_blocklist(blocklist_file)
    disposable_domains = load_disposable_domains(disposable_file)

    processed_files = load_checkpoint()
    all_files = [f for f in get_all_files(folder) if f not in processed_files]
    temp_dir = tempfile.mkdtemp()
    manager = multiprocessing.Manager()
    queue = manager.Queue()

    writer_thread = threading.Thread(target=writer, args=(queue, email_out, url_out, csv_out))
    writer_thread.start()

    try:
        with tqdm(total=len(all_files), desc="Scanning files", unit="file") as pbar, \
             ProcessPoolExecutor(max_workers=num_processes) as executor:

            futures = {executor.submit(process_file, f, forbidden_words, disposable_domains, block_patterns, temp_dir): f for f in all_files}
            for future in as_completed(futures):
                try:
                    emails, urls, extracted_files, src_file = future.result()
                    queue.put((emails, urls, src_file))
                    processed_files.add(src_file)
                    save_checkpoint(processed_files)
                    for efp in extracted_files:
                        if os.path.isfile(efp):
                            all_files.append(efp)
                            pbar.total += 1
                except Exception as e:
                    print(f"[ERROR]: {e}")
                finally:
                    pbar.update(1)
        queue.put('DONE')
        writer_thread.join()

        print("\nSummary:")
        print(f"Total files processed: {len(processed_files)}")
        print(f"Results written instantly. Check '{email_out}' and '{url_out}'.")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Universal Email & URL Extractor (Real-time, Multiprocessing, Dedup by Domain, Clean URLs)")
    parser.add_argument('folder', help='Folder to scan')
    parser.add_argument('-o', '--output', default='emails_found.txt', help='Output file for emails')
    parser.add_argument('-u', '--url_output', default='urls_found.txt', help='Output file for URLs')
    parser.add_argument('-c', '--csv_output', default=None, help='CSV output file (optional)')
    parser.add_argument('-b', '--blocklist', default='blocked_domains.txt', help='Blocked domains file')
    parser.add_argument('-d', '--disposable', default='disposable_domains.txt', help='Disposable domains file')
    parser.add_argument('-f', '--forbidden', nargs='*', default=['user', 'test', 'demo', 'example', 'sample', 'dummy', 'temp', 'trial', 'no-reply', 'noreply'], help='Forbidden words in emails')
    parser.add_argument('-p', '--processes', type=int, default=4, help='Number of processes to use')
    args = parser.parse_args()

    main(args.folder, args.output, args.url_output, args.csv_output, args.blocklist, args.disposable, args.forbidden, num_processes=args.processes)
