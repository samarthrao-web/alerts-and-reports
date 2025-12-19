import json
import imaplib
import email
import os
from datetime import datetime

# --- CONFIGURATION ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'samarth.rao@juspay.in'
EMAIL_PASS = 'jpycuyqbeetegwxy'
QUEUE_FILE = 'job_queue.json'
SUCCESS_FILE = 'success.json'
DOWNLOAD_FOLDER = 'std_report_downloaded'

# Ensure download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def download_attachment(mail_instance, subject_to_find, task_uid):
    """
    Searches for email, checks body for task_uid, and downloads attachment.
    """
    try:
        search_query = f'SUBJECT "{subject_to_find}"'
        status, messages = mail_instance.search(None, search_query)

        if status != 'OK' or not messages[0]:
            return False

        for num in messages[0].split():
            status, data = mail_instance.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            email_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            email_body += payload.decode(errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    email_body = payload.decode(errors='ignore')

            # Check if task_uid is in the email body
            if task_uid in email_body:
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            save_path = os.path.join(
                                DOWNLOAD_FOLDER, f"{task_uid}_{filename}")
                            with open(save_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            return True
        return False
    except Exception as e:
        return False


def process_full_queue():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(QUEUE_FILE):
        print(f"[{timestamp}] ⚠️ File job_queue.json not found.")
        return

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    if not queue:
        print(f"[{timestamp}] ℹ️ Queue is empty. Nothing to process.")
        return

    still_pending = []
    new_successes = []

    print(f"\n[{timestamp}] --- Cron Run Started: Checking {len(queue)} pairs ---")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        for task in queue:
            name_old = task['task_name_old']
            uid_old = task['task_uid_old']
            name_new = task['task_name_new']
            uid_new = task['task_uid_new']

            # Attempt downloads
            old_res = download_attachment(mail, name_old, uid_old)
            new_res = download_attachment(mail, name_new, uid_new)

            if old_res and new_res:
                # LOG AS FOUND
                print(
                    f"✅ FOUND: {name_old} (Both reports downloaded and matched)")
                new_successes.append(task)
            else:
                # LOG AS NOT FOUND with specific details
                status_old = "FOUND" if old_res else "NOT FOUND"
                status_new = "FOUND" if new_res else "NOT FOUND"
                print(
                    f"❌ NOT FOUND: {name_old} (OLD: {status_old}, NEW: {status_new})")
                still_pending.append(task)

        mail.logout()
    except Exception as e:
        print(f"❌ Session Error: {e}")
        return

    # Update success.json
    if new_successes:
        success_list = []
        if os.path.exists(SUCCESS_FILE):
            with open(SUCCESS_FILE, 'r') as f:
                try:
                    success_list = json.load(f)
                except:
                    success_list = []
        success_list.extend(new_successes)
        with open(SUCCESS_FILE, 'w') as f:
            json.dump(success_list, f, indent=4)

    # Update job_queue.json
    with open(QUEUE_FILE, 'w') as f:
        json.dump(still_pending, f, indent=4)

    print(f"[{timestamp}] --- Run Complete: {len(new_successes)} FOUND, {len(still_pending)} PENDING ---\n")


if __name__ == "__main__":
    process_full_queue()
