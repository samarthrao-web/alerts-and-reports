# report_consumer.py (Continuous Daemon Version)

import json
import os
import time
import imaplib
import email
from email.header import decode_header
import sys
import signal

# --- CONFIGURATION ---
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "your_actual_app_password" # <-- Set this securely!
DOWNLOAD_DIR_NAME = "downloaded_reports"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE_PATH = os.path.join(BASE_DIR, "job_queue.json")
DOWNLOAD_PATH = os.path.join(BASE_DIR, DOWNLOAD_DIR_NAME)

# Daemon Control Flag
exit_now = False

def exit_gracefully(signum, frame):
    """Handles graceful shutdown when Systemd sends SIGTERM."""
    global exit_now
    print(f"\n[{time.ctime()}] Received signal {signum}. Shutting down consumer...")
    exit_now = True

def load_queue():
    """Loads the queue state from the JSON file."""
    if not os.path.exists(QUEUE_FILE_PATH):
        return []
    try:
        with open(QUEUE_FILE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[{time.ctime()}] ❌ Error loading queue file: {e}")
        return []

def save_queue(queue_data):
    """Saves the updated queue state."""
    try:
        with open(QUEUE_FILE_PATH, 'w') as f:
            json.dump(queue_data, f, indent=4)
    except Exception as e:
        print(f"[{time.ctime()}] ❌ Error saving queue file: {e}")
        
def download_attachment(mail, latest_email_id, job_id):
    """Fetches the email, downloads the attachment, and marks as seen."""
    # (Implementation remains the same as previous answer, omitted here for brevity)
    # ...
    # Placeholder implementation:
    print(f"  -> Downloading report for {job_id}...")
    try:
        # Code to fetch and save the attachment goes here
        # ... mail.fetch, email.message_from_bytes, os.makedirs, with open(filepath, "wb") ...
        mail.store(latest_email_id, '+FLAGS', r'\Seen')
        return True
    except Exception as e:
        print(f"❌ Download/Save failed: {e}")
        return False

def process_queue_item(job_id):
    """Connects to IMAP and searches for the specific job ID."""
    try:
        # Connect
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Search for UNSEEN emails containing the job ID string
        search_criteria = f'(UNSEEN TEXT "{job_id}")'
        status, messages = mail.search(None, search_criteria)
        
        if status != "OK" or not messages[0]:
            return False # Not found
        
        email_ids = messages[0].split()
        latest_email_id = email_ids[-1]
        
        print(f"  -> Match found! Email ID: {latest_email_id}")
        
        return download_attachment(mail, latest_email_id, job_id)

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False
    finally:
        try:
            if 'mail' in locals() and mail:
                mail.close()
                mail.logout()

# --- MAIN DAEMON LOOP ---

def run_daemon_consumer():
    """The main loop for the continuous consumer."""
    
    # 1. Set up signal handlers
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    
    # 2. Continuous Loop
    while not exit_now:
        
        queue = load_queue()
        
        if not queue:
            # Queue is empty, sleep longer and check again
            print(f"[{time.ctime()}] Queue empty. Sleeping 60s...")
            time.sleep(60)
            continue

        # 3. Process the Head of the Queue (FIFO)
        queue_item = queue[0]
        dim_name = queue_item.get('dimensions_name', 'N/A')
        old_id = queue_item.get('old_api_job_id')
        new_id = queue_item.get('new_api_job_id')
        
        print(f"\n[{time.ctime()}] >>> Checking Job for Dimension: {dim_name}")
        
        processed_success = False
        
        # Try to process OLD ID first
        if old_id:
            print(f"[{time.ctime()}] Attempting OLD API job ID: {old_id}")
            processed_success = process_queue_item(old_id)
        
        # If OLD ID failed, try NEW ID
        if not processed_success and new_id:
            print(f"[{time.ctime()}] Attempting NEW API job ID: {new_id}")
            processed_success = process_queue_item(new_id)

        # 4. Update the Queue State
        if processed_success:
            queue.pop(0) # Remove the processed item
            save_queue(queue)
            print(f"[{time.ctime()}] *** Item {dim_name} fully processed and removed. Remaining: {len(queue)}")
            time.sleep(10) # Pause briefly before tackling the next item
        else:
            # Email not found yet, keep the item at the head and wait
            print(f"[{time.ctime()}] *** Item {dim_name} not ready. Sleeping 30s...")
            time.sleep(30) # Check for the same email again soon

    print(f"[{time.ctime()}] Daemon finished.")

if __name__ == "__main__":
    run_daemon_consumer()