import os
import re
import csv
import json
import time
import logging
import tldextract
import idna
from urllib.parse import urlparse
import requests

CHECKPOINT_FILE = 'checkpoint.json'

def idna_email(email):
    if '@' in email:
        local, domain = email.rsplit('@', 1)
        try:
            domain_idna = idna.encode(domain).decode('ascii')
            return f"{local}@{domain_idna}"
        except Exception:
            return email  # fallback: return as-is if IDNA fails
    return email

def get_root_domain(url):
    ext = tldextract.extract(url)
    if not ext.domain or not ext.suffix:
        return None
    return f"{ext.domain}.{ext.suffix}"

def get_subdomain(url):
    ext = tldextract.extract(url)
    if ext.subdomain:
        return f"{ext.subdomain}.{ext.domain}.{ext.suffix}"
    elif ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    else:
        return None

def get_clean_base_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc.encode('idna').decode('utf-8')  # IDN support
    return f"{parsed.scheme}://{netloc}"

def extract_urls(text, url_regex=None):
    urls = set()
    # Use custom regex if provided
    if url_regex:
        pattern = re.compile(url_regex)
        for match in pattern.finditer(text):
            url = match.group(0).rstrip('.,;\'"!?)]}')
            if len(url) > 10 and '.' in url:
                urls.add(url)
        return urls
    # Default: robust, concatenated URL extraction
    pattern = re.compile(r'https?://')
    starts = [m.start() for m in pattern.finditer(text)]
    for i, start in enumerate(starts):
        end = starts[i+1] if i+1 < len(starts) else len(text)
        snippet = text[start:end]
        m = re.match(r'(https?://[^\s\'",<>$$$${}()|]+)', snippet)
        if m:
            url = m.group(1).rstrip('.,;\'"!?)]}')
            if len(url) > 10 and '.' in url:
                urls.add(url)
    return urls

def extract_emails(text, email_regex=None):
    if email_regex:
        pattern = re.compile(email_regex)
    else:
        pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    return set(pattern.findall(text))

def get_all_files(folder, include_ext=None, exclude_ext=None):
    for root, _, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            yield path

def read_text_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''

def validate_url_status(url, timeout=5):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_checkpoint(processed):
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed), f)

def real_extractor(
    input_folder,
    output_folder,
    email_file,
    url_file,
    map_file,
    blocklist_path,
    disposable_path,
    include_ext,
    exclude_ext,
    url_mode,
    processes,
    validate_urls,
    checkpointing,
    enable_mapping,
    log_callback,
    email_callback,
    url_callback,
    stop_signal,
    url_regex=None,
    email_regex=None
):
    # Prepare sets for deduplication
    all_emails = set()
    all_urls = set()
    domain_to_urls = dict()
    subdomain_to_urls = dict()
    rootdomain_to_urls = dict()
    processed_files = load_checkpoint() if checkpointing else set()

    # File extension normalization
    include_ext = set([e if e.startswith('.') else '.'+e for e in include_ext]) if include_ext else None
    exclude_ext = set([e if e.startswith('.') else '.'+e for e in exclude_ext]) if exclude_ext else None

    files = [f for f in get_all_files(input_folder, include_ext, exclude_ext) if not checkpointing or f not in processed_files]
    total_files = len(files)
    log_callback(f"Found {total_files} files to process.")

    t0 = time.time()
    for i, path in enumerate(files):
        if stop_signal[0]:
            log_callback(f"Extraction stopped by user at file {i+1}.")
            break
        text = read_text_file(path)
        emails = extract_emails(text, email_regex)
        emails = {idna_email(e) for e in emails}
        # Filtering by blocklist/disposable can be added here if needed
        for e in emails:
            if e not in all_emails:
                all_emails.add(e)
                email_callback(e)
        urls = extract_urls(text, url_regex)
        valid_urls = set()
        for url in urls:
            base_url = get_clean_base_url(url)
            if validate_urls and not validate_url_status(base_url):
                log_callback(f"URL failed validation (not live): {base_url} (from {path})")
                continue
            valid_urls.add(base_url)
        for url in valid_urls:
            if url not in all_urls:
                all_urls.add(url)
                url_callback(url)
        # Mapping logic
        for url in valid_urls:
            root = get_root_domain(url)
            subd = get_subdomain(url)
            if root:
                rootdomain_to_urls.setdefault(root, set()).add(url)
            if subd:
                subdomain_to_urls.setdefault(subd, set()).add(url)
            domain_to_urls.setdefault(url, set()).add(url)
        if checkpointing:
            processed_files.add(path)
            save_checkpoint(processed_files)
        if i % 10 == 0:
            log_callback(f"Processed {i+1}/{total_files} files...")

    t1 = time.time()
    export_urls = set()
    if url_mode == "root":
        for urls in rootdomain_to_urls.values():
            export_urls.add(next(iter(urls)))
    elif url_mode == "subdomain":
        for urls in subdomain_to_urls.values():
            export_urls.add(next(iter(urls)))
    elif url_mode == "all":
        export_urls = set(domain_to_urls.keys())

    # Mapping output (if enabled)
    if enable_mapping and map_file:
        mapping = {}
        if url_mode == "root":
            mapping = {k: list(v) for k, v in rootdomain_to_urls.items()}
        elif url_mode == "subdomain":
            mapping = {k: list(v) for k, v in subdomain_to_urls.items()}
        elif url_mode == "all":
            mapping = {k: list(v) for k, v in domain_to_urls.items()}
        with open(os.path.join(output_folder, map_file), 'w', encoding='utf-8') as mf:
            if map_file.endswith('.json'):
                json.dump(mapping, mf, indent=2)
            else:
                writer = csv.writer(mf)
                writer.writerow(['Domain/Subdomain', 'URLs'])
                for k, v in mapping.items():
                    writer.writerow([k, "; ".join(v)])
        log_callback(f"Mapping written to: {os.path.join(output_folder, map_file)}")

    # Save results
    with open(os.path.join(output_folder, email_file), 'w', encoding='utf-8') as ef:
        for e in sorted(all_emails):
            ef.write(e + '\n')
    with open(os.path.join(output_folder, url_file), 'w', encoding='utf-8') as uf:
        for u in sorted(export_urls):
            uf.write(u + '\n')
    log_callback(f"Emails written to: {os.path.join(output_folder, email_file)}")
    log_callback(f"URLs written to: {os.path.join(output_folder, url_file)}")
    elapsed = t1 - t0
    log_callback(f"Extraction complete. Time taken: {elapsed:.2f} seconds. Files processed: {len(files)}.")
