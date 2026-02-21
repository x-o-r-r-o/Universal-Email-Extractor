import streamlit as st
import os
import threading
import pandas as pd
import time

# --- Import your real_extractor from the backend file ---
from streamlit_extractor_backend import real_extractor

def list_subdirs(path):
    try:
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    except Exception:
        return []

def list_files(path):
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except Exception:
        return []

st.set_page_config(page_title="Universal Extractor PRO", layout="wide")

menu = st.sidebar.radio(
    "Navigation",
    ["Extraction", "Results", "Logs", "Settings"],
    index=0,
)

st.title("Universal Email & URL Extractor PRO")

# --- Session State Initialization ---
for key, default in [
    ('extraction_running', False),
    ('progress', 0),
    ('stats', {
        "files_processed": 0,
        "emails_found": 0,
        "urls_found": 0,
        "start_time": None,
        "elapsed": 0.0
    }),
    ('stop_signal', False),
    ('emails', []),
    ('urls', []),
    ('logs', [])
]:
    if key not in st.session_state:
        st.session_state[key] = default

def log_callback(msg):
    st.session_state.logs.append(msg)
    st.experimental_rerun()  # Force UI update for instant log refresh

def email_callback(email):
    if email not in st.session_state.emails:
        st.session_state.emails.append(email)
        st.session_state.stats["emails_found"] = len(st.session_state.emails)
        st.experimental_rerun()

def url_callback(url):
    if url not in st.session_state.urls:
        st.session_state.urls.append(url)
        st.session_state.stats["urls_found"] = len(st.session_state.urls)
        st.experimental_rerun()

def run_extractor_thread(
    input_folder, output_folder, email_file, url_file, map_file,
    blocklist_path, disposable_path, include_ext, exclude_ext,
    url_mode, processes, validate_urls, checkpointing, enable_mapping,
    url_regex, email_regex
):
    st.session_state.stats = {
        "files_processed": 0,
        "emails_found": 0,
        "urls_found": 0,
        "start_time": time.time(),
        "elapsed": 0.0
    }
    st.session_state.progress = 0
    st.session_state.emails = []
    st.session_state.urls = []
    st.session_state.logs = []
    stop_signal = [False]
    st.session_state._stop_signal_ref = stop_signal  # Save for UI stop button

    real_extractor(
        input_folder,
        output_folder,
        email_file,
        url_file,
        map_file,
        blocklist_path,
        disposable_path,
        [e.strip() for e in include_ext.split(",") if e.strip()],
        [e.strip() for e in exclude_ext.split(",") if e.strip()],
        url_mode,
        processes,
        validate_urls,
        checkpointing,
        enable_mapping,
        log_callback,
        email_callback,
        url_callback,
        stop_signal,
        url_regex,
        email_regex
    )
    st.session_state.extraction_running = False
    st.session_state.stop_signal = False
    st.session_state.logs.append("Extraction thread finished.")
    st.experimental_rerun()

if menu == "Extraction":
    st.header("Extraction Controls")

    st.subheader("1. Select Input Data Folder")
    root_dir = st.text_input("Root directory to browse", value=os.path.expanduser("~"), disabled=st.session_state.extraction_running)
    subdirs = list_subdirs(root_dir) if os.path.isdir(root_dir) else []
    input_folder = st.selectbox("Choose input folder", options=[""] + subdirs, disabled=st.session_state.extraction_running)
    full_input_path = os.path.join(root_dir, input_folder) if input_folder else ""

    if full_input_path and os.path.isdir(full_input_path):
        st.success(f"Selected: {full_input_path}")
    else:
        st.info("Pick a folder above or enter a valid root directory.")

    st.subheader("2. Select Output Folder and Filenames")
    out_root_dir = st.text_input("Root directory to browse for output", value=os.path.expanduser("~"), disabled=st.session_state.extraction_running)
    out_subdirs = list_subdirs(out_root_dir) if os.path.isdir(out_root_dir) else []
    output_folder = st.selectbox("Choose output folder", options=[""] + out_subdirs, disabled=st.session_state.extraction_running)
    full_output_path = os.path.join(out_root_dir, output_folder) if output_folder else ""

    if full_output_path and os.path.isdir(full_output_path):
        st.success(f"Selected: {full_output_path}")
    else:
        st.info("Pick a folder above or enter a valid output root directory.")

    email_file = st.text_input("Email output filename", value="emails_found.txt", disabled=st.session_state.extraction_running)
    url_file = st.text_input("URL output filename", value="urls_found.txt", disabled=st.session_state.extraction_running)
    map_file = st.text_input("Mapping output filename (optional)", value="", disabled=st.session_state.extraction_running)

    st.subheader("3. Blocked/Disposable Domains Files")
    blocklist_uploaded = st.file_uploader("Upload blocked domains file (optional)", type=["txt"], key="blocklist", disabled=st.session_state.extraction_running)
    disposable_uploaded = st.file_uploader("Upload disposable domains file (optional)", type=["txt"], key="disposable", disabled=st.session_state.extraction_running)
    blocklist_files = list_files(full_input_path) if os.path.isdir(full_input_path) else []
    blocklist_file = st.selectbox("Or select blocked domains file", options=[""] + blocklist_files, disabled=st.session_state.extraction_running)
    disposable_files = list_files(full_input_path) if os.path.isdir(full_input_path) else []
    disposable_file = st.selectbox("Or select disposable domains file", options=[""] + disposable_files, disabled=st.session_state.extraction_running)

    st.subheader("4. Extraction Options")
    col3, col4 = st.columns(2)
    with col3:
        include_ext = st.text_input("File extensions to include (comma-separated, e.g. .txt,.csv)", value="", disabled=st.session_state.extraction_running)
        exclude_ext = st.text_input("File extensions to exclude (comma-separated, e.g. .exe,.bin)", value="", disabled=st.session_state.extraction_running)
    with col4:
        url_mode = st.selectbox("URL deduplication/export mode", ["root", "subdomain", "all"], index=0, disabled=st.session_state.extraction_running)
        processes = st.number_input("Number of parallel processes", min_value=1, max_value=32, value=4, disabled=st.session_state.extraction_running)
        url_regex = st.text_input("Custom URL regex (optional)", value="", disabled=st.session_state.extraction_running)
        email_regex = st.text_input("Custom Email regex (optional)", value="", disabled=st.session_state.extraction_running)

    st.subheader("5. Advanced Options")
    colA, colB, colC = st.columns(3)
    with colA:
        validate_urls = st.checkbox("Enable URL validation", value=False, disabled=st.session_state.extraction_running)
    with colB:
        checkpointing = st.checkbox("Enable checkpointing", value=True, disabled=st.session_state.extraction_running)
    with colC:
        enable_mapping = st.checkbox("Enable mapping export", value=False, disabled=st.session_state.extraction_running)

    st.markdown("---")

    col_run, col_stop = st.columns([1, 1])
    with col_run:
        if st.button("Start Extraction", disabled=st.session_state.extraction_running):
            st.session_state.extraction_running = True
            st.session_state.stop_signal = False
            threading.Thread(
                target=run_extractor_thread,
                args=(
                    full_input_path, full_output_path, email_file, url_file, map_file,
                    blocklist_file, disposable_file, include_ext, exclude_ext,
                    url_mode, processes, validate_urls, checkpointing, enable_mapping,
                    url_regex, email_regex
                ),
                daemon=True
            ).start()
    with col_stop:
        if st.button("Stop Extraction", disabled=not st.session_state.extraction_running):
            if hasattr(st.session_state, '_stop_signal_ref'):
                st.session_state._stop_signal_ref[0] = True

    st.subheader("Live Progress")
    stats = st.session_state.stats
    st.progress(st.session_state.progress)
    st.write(f"Files processed: {stats['files_processed']}")
    st.write(f"Emails found: {stats['emails_found']}")
    st.write(f"URLs found: {stats['urls_found']}")
    st.write(f"Elapsed time: {stats['elapsed']:.2f} seconds")
    speed = stats['files_processed'] / stats['elapsed'] if stats['elapsed'] > 0 else 0
    st.write(f"Speed: {speed:.2f} files/sec")

    st.subheader("Summary Table")
    st.table({
        "Metric": ["Files Processed", "Emails Found", "URLs Found", "Elapsed Time (s)", "Speed (files/sec)"],
        "Value": [
            stats['files_processed'],
            stats['emails_found'],
            stats['urls_found'],
            f"{stats['elapsed']:.2f}",
            f"{speed:.2f}"
        ]
    })

elif menu == "Results":
    st.header("Results")
    st.subheader("Extracted Emails")
    df_emails = pd.DataFrame(st.session_state.emails, columns=["Email"])
    st.dataframe(df_emails)
    st.download_button("Download Emails as CSV", df_emails.to_csv(index=False), "emails.csv")

    st.subheader("Extracted URLs")
    df_urls = pd.DataFrame(st.session_state.urls, columns=["URL"])
    st.dataframe(df_urls)
    st.download_button("Download URLs as CSV", df_urls.to_csv(index=False), "urls.csv")

elif menu == "Logs":
    st.header("Logs")
    if st.button("Update Blocklists/Disposable (Simulated)"):
        st.session_state.logs.append("Blocklists/disposable domains updated from trusted sources.")
    st.subheader("Live Log Output")
    for log in st.session_state.logs[-50:]:
        st.text(log)

elif menu == "Settings":
    st.header("Settings & Advanced Options")
    st.info("Advanced configuration and blocklist management are now in Extraction and Logs tabs.")

st.markdown("---")
st.caption("Full backend integration: extraction, live logs, live results.")
