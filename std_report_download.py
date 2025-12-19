import json
import imaplib
import email
import os

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
    Searches for email, checks body/filename for task_uid, and downloads attachment.
    """
    try:
        # Search specifically in the SUBJECT field
        search_query = f'SUBJECT "{subject_to_find}"'
        status, messages = mail_instance.search(None, search_query)

        if status != 'OK' or not messages[0]:
            return False

        # Iterate through messages found (in case there are multiple)
        for num in messages[0].split():
            status, data = mail_instance.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Check if task_uid is in the email body or filename
            email_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        email_body += str(part.get_payload(decode=True))
            else:
                email_body = str(msg.get_payload(decode=True))

            # Logic: If UID is in the body, proceed to download attachments
            if task_uid in email_body:
                print(f"      🎯 UID {task_uid} matched for {subject_to_find}")

                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            # Prepend task_uid to filename to keep it unique
                            save_path = os.path.join(
                                DOWNLOAD_FOLDER, f"{task_uid}_{filename}")
                            with open(save_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            print(f"      💾 Saved: {save_path}")
                            return True
        return False
    except Exception as e:
        print(f"   ❌ Download Error: {e}")
        return False


def process_full_queue():
    if not os.path.exists(QUEUE_FILE):
        print("File job_queue.json not found.")
        return

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    if not queue:
        print("Queue is empty.")
        return

    still_pending = []
    new_successes = []

    # Login ONCE for the entire process
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        for task in queue:
            name_old = task['task_name_old']
            uid_old = task['task_uid_old']
            name_new = task['task_name_new']
            uid_new = task['task_uid_new']

            print(f"🧐 Checking pair: {name_old} & {name_new}")

            # Try to download OLD report
            old_downloaded = download_attachment(mail, name_old, uid_old)

            # Try to download NEW report
            new_downloaded = download_attachment(mail, name_new, uid_new)

            if old_downloaded and new_downloaded:
                print(f"   ✅ BOTH DOWNLOADED! Moving to success.")
                new_successes.append(task)
            else:
                print(f"   ⏳ NOT READY/UID MISMATCH: Keeping in queue.")
                still_pending.append(task)

        mail.logout()
    except Exception as e:
        print(f"❌ Login/Session Error: {e}")
        return

    # 1. Update success.json
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

    # 2. Update job_queue.json
    with open(QUEUE_FILE, 'w') as f:
        json.dump(still_pending, f, indent=4)

    print(
        f"\n📝 Run Complete. {len(new_successes)} pairs downloaded. {len(still_pending)} pending.")


if __name__ == "__main__":
    process_full_queue()
