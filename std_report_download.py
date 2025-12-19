import json
import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime

# --- CONFIGURATION ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'samarth.rao@juspay.in'
EMAIL_PASS = 'jpycuyqbeetegwxy'
QUEUE_FILE = 'job_queue.json'
SUCCESS_FILE = 'success.json'
DOWNLOAD_FOLDER = 'std_report_downloaded'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def check_subject_exists(mail_instance, subject_to_find):
    """Step 1: Quick check if any email exists with this subject."""
    try:
        mail_instance.select("inbox")
        search_query = f'(SUBJECT "{subject_to_find}")'
        status, search_data = mail_instance.search(None, search_query)
        email_ids = search_data[0].split()
        return email_ids if status == 'OK' and email_ids else []
    except Exception:
        return []


def verify_uid_and_download(mail_instance, email_ids, task_uid):
    """Step 2: Only runs if subjects were found. Verifies UID and downloads."""
    try:
        # Check the most recent emails matching the subject first
        for msg_id in reversed(email_ids):
            status, data = mail_instance.fetch(msg_id, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract body to check for UID
            email_body = ""
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        email_body += payload.decode(errors='ignore')

            uid_in_body = task_uid in email_body

            # Check attachments
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    # Match if UID is in filename OR body
                    if filename and (task_uid in filename or uid_in_body):
                        save_path = os.path.join(
                            DOWNLOAD_FOLDER, f"{task_uid}_{filename}")
                        with open(save_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        return True
        return False
    except Exception:
        return False


def process_full_queue():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(QUEUE_FILE):
        return

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    if not queue:
        print(f"[{timestamp}] ℹ️ Queue is empty.")
        return

    still_pending = []
    new_successes = []

    print(f"[{timestamp}] --- Cron Run Started ---")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)

        for task in queue:
            name_old = task.get('task_name_old')
            uid_old = task.get('task_uid_old')
            name_new = task.get('task_name_new')
            uid_new = task.get('task_uid_new')

            # STEP 1: Fast Search for Subjects
            old_ids = check_subject_exists(mail, name_old)
            new_ids = check_subject_exists(mail, name_new)

            print(f"{name_old} = {'SUBJECT FOUND' if old_ids else 'NOT FOUND'}")
            print(f"{name_new} = {'SUBJECT FOUND' if new_ids else 'NOT FOUND'}")

            # STEP 2: Only proceed to UID check and Download if BOTH subjects exist
            if old_ids and new_ids:
                print(f"   🔎 Both subjects located. Verifying UIDs and downloading...")

                old_success = verify_uid_and_download(mail, old_ids, uid_old)
                new_success = verify_uid_and_download(mail, new_ids, uid_new)

                if old_success and new_success:
                    print(f"✅ PAIR COMPLETED: Moving to success.json")
                    new_successes.append(task)
                else:
                    print(
                        f"❌ UID MISMATCH: (Old UID Found: {old_success}, New UID Found: {new_success})")
                    still_pending.append(task)
            else:
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

    print(f"--- Run Complete ---\n")


if __name__ == "__main__":
    process_full_queue()
