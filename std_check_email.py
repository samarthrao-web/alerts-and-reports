import json
import imaplib
import email
import os

# --- CONFIGURATION ---
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'samarth.rao@juspay.in'
# Use an App Password, not your login password
EMAIL_PASS = 'EMAIL_PASSWORD' = "jpycuyqbeetegwxy"
QUEUE_FILE = 'job_queue.json'
SUCCESS_FILE = 'success.json'


def check_job_in_email(job_id):
    """Searches the inbox for a specific Job ID in the email body."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Search for the Job ID string in the entire mailbox
        status, messages = mail.search(None, f'BODY "{job_id}"')

        if status == 'OK' and messages[0]:
            return True
        return False
    except Exception as e:
        print(f"Error checking email: {e}")
        return False
    finally:
        mail.logout()


def process_queue():
    if not os.path.exists(QUEUE_FILE):
        print("Queue file not found.")
        return

    with open(QUEUE_FILE, 'r') as f:
        queue = json.load(f)

    if not queue:
        print("Queue is empty.")
        return

    # Look at the first pair in the list (FIFO)
    current_task = queue[0]
    task_name = current_task['task_name']
    old_id = current_task['old_job_id']
    new_id = current_task['new_job_id']

    print(f"Checking status for: {task_name}")

    # Check if BOTH IDs have arrived in email
    old_found = check_job_in_email(old_id)
    new_found = check_job_in_email(new_id)

    if old_found and new_found:
        print(f"✅ Both IDs found for {task_name}. Moving to success.")

        # 1. Load/Create success.json
        success_list = []
        if os.path.exists(SUCCESS_FILE):
            with open(SUCCESS_FILE, 'r') as f:
                success_list = json.load(f)

        # 2. Add to success
        success_list.append(current_task)
        with open(SUCCESS_FILE, 'w') as f:
            json.dump(success_list, f, indent=4)

        # 3. Remove from queue
        queue.pop(0)
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=4)
    else:
        print(f"⏳ Waiting for reports... (Old: {old_found}, New: {new_found})")


if __name__ == "__main__":
    process_queue()
