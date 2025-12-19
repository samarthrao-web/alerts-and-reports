import json
import imaplib
import os

# --- CONFIGURATION ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'samarth.rao@juspay.in'
EMAIL_PASS = 'jpycuyqbeetegwxy'
QUEUE_FILE = 'job_queue.json'
SUCCESS_FILE = 'success.json'


def search_email_by_subject(subject_to_find):
    """Connects to IMAP and searches for an email with the exact subject."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Search specifically in the SUBJECT field
        search_query = f'SUBJECT "{subject_to_find}"'
        status, messages = mail.search(None, search_query)

        if status == 'OK' and messages[0]:
            return True
        return False
    except Exception as e:
        print(f"   ❌ IMAP Error: {e}")
        return False
    finally:
        try:
            mail.logout()
        except:
            pass


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

    # Loop through EVERY item in the JSON list
    for task in queue:
        name_old = task['task_name_old']
        name_new = task['task_name_new']

        print(f"🧐 Checking pair: {name_old} & {name_new}")

        old_found = search_email_by_subject(name_old)
        new_found = search_email_by_subject(name_new)

        if old_found and new_found:
            print(f"   ✅ BOTH FOUND! Moving to success.")
            new_successes.append(task)
        else:
            print(
                f"   ⏳ NOT READY: (OLD: {old_found}, NEW: {new_found}). Keeping in queue.")
            still_pending.append(task)

    # 1. Update success.json if we found anything new
    if new_successes:
        success_list = []
        if os.path.exists(SUCCESS_FILE):
            try:
                with open(SUCCESS_FILE, 'r') as f:
                    success_list = json.load(f)
            except:
                success_list = []

        success_list.extend(new_successes)
        with open(SUCCESS_FILE, 'w') as f:
            json.dump(success_list, f, indent=4)

    # 2. Update job_queue.json with only the items that were NOT found
    with open(QUEUE_FILE, 'w') as f:
        json.dump(still_pending, f, indent=4)

    print(
        f"\n📝 Run Complete. {len(new_successes)} reports moved to success. {len(still_pending)} remain in queue.")


if __name__ == "__main__":
    process_full_queue()
