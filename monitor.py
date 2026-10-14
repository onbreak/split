import datetime
import hashlib
import csv
import os
import requests

FILE_URL = "https://tssi.ro/uploads/Proiect-de-divizare-TSSI.pdf"
LOG_FILE = "30_day_monitoring_report.csv"
EXPECTED_HASH = None  # Replace with known SHA-256 string, or set automatically on first run

def get_file_hash(content):
    return hashlib.sha256(content).hexdigest()

def check_file():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status_code = None
    uptime = "DOWN"
    file_hash = "N/A"
    hash_matched = "N/A"
    error_msg = ""

    try:
        response = requests.get(FILE_URL, timeout=15)
        status_code = response.status_code
        if response.status_code == 200:
            uptime = "UP"
            file_hash = get_file_hash(response.content)
            
            global EXPECTED_HASH
            if EXPECTED_HASH is None:
                EXPECTED_HASH = file_hash  # Baseline recorded on initial run
                
            hash_matched = "YES" if file_hash == EXPECTED_HASH else "CHANGED"
        else:
            error_msg = f"HTTP Status {status_code}"
    except Exception as e:
        error_msg = str(e)

    # Initialize CSV header if file doesn't exist
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Status Code", "Uptime", "SHA256 Hash", "Hash Unchanged?", "Notes"])
        writer.writerow([now, status_code, uptime, file_hash, hash_matched, error_msg])

if __name__ == "__main__":
    check_file()
