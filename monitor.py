import datetime
import hashlib
import csv
import os
import requests
import urllib3

# Suppress the insecure request warning to keep logs clean
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FILE_URL = "https://tssi.ro/uploads/Proiect-de-divizare-TSSI.pdf"
LOG_FILE = "30_day_monitoring_report.csv"

def get_file_hash(content):
    return hashlib.sha256(content).hexdigest()

def get_expected_hash():
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 4 and row[3] not in ("N/A", "Error"):
                return row[3]
    return None

def check_file():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status_code = "Error"
    uptime = "DOWN"
    file_hash = "N/A"
    hash_matched = "N/A"
    error_msg = ""

    expected_hash = get_expected_hash()

    try:
        # Added verify=False to bypass the SSL certificate error
        response = requests.get(FILE_URL, timeout=15, verify=False)
        status_code = response.status_code
        if response.status_code == 200:
            uptime = "UP"
            file_hash = get_file_hash(response.content)
            
            if expected_hash is None:
                hash_matched = "BASELINE SET"
            else:
                hash_matched = "YES" if file_hash == expected_hash else "CHANGED"
        else:
            error_msg = f"HTTP Status {status_code}"
    except Exception as e:
        error_msg = str(e)

    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)", "Status Code", "Uptime", "SHA256 Hash", "Hash Unchanged?", "Notes"])
        writer.writerow([now, status_code, uptime, file_hash, hash_matched, error_msg])

if __name__ == "__main__":
    check_file()
