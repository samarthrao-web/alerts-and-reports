import imaplib
import email
from email.header import decode_header
import os
import sys
import time # Only used for timestamp in prints

# --- CONFIGURATION ---
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "jpycuyqbeetegwxy"  # <-- REQUIRED: Replace with your 16-character App Password
SUBJECT_KEYWORD = "testingchange1"

# Directory where reports will be saved (relative to where you run the script)
DOWNLOAD_DIR_NAME = "juspay_reports"
DOWNLOAD_PATH = os.path.join(os.getcwd(), DOWNLOAD_DIR_NAME) # Uses current working directory

def search_and_download_report():
    """Connects to Gmail, searches for the report, and downloads the attachment."""
    
    print(f"\n[{time.ctime()}] {'='*70}")
    print("📧 Starting Email Report Extraction...")
    print(f"{'='*70}")
    
    # 1. Connect to Gmail
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("✅ Successfully connected to Gmail")
        
        # 2. Select the INBOX
        mail.select("inbox")
        
        # 3. Search for ALL emails with the specific subject (including already read ones)
        # Change ALL to UNSEEN if you want to process only unread emails
        search_criteria = f'(TEXT "{SUBJECT_KEYWORD}")'
        status, messages = mail.search(None, search_criteria)
        
        if status != "OK":
            print(f"❌ Search failed with status: {status}")
            return
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print(f"🔍 No NEW emails found with subject '{SUBJECT_KEYWORD}'.")
            return
        
        print(f"✅ Found {len(email_ids)} new email(s). Processing the latest one...")
        
        # Process the latest email (last ID in the list)
        latest_email_id = email_ids[-1]
        
        # Fetch the email
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        if status != "OK":
            print(f"❌ Failed to fetch email ID {latest_email_id}")
            return
        
        # Parse email
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        # Extract details
        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes): subject = subject.decode()
        from_email = email_message.get("From")
        
        print(f"{'-'*70}")
        print(f"📨 Email Details:")
        print(f"Subject: {subject}")
        print(f"From: {from_email}")
        print(f"{'-'*70}")

        # Extract email body to find download links
        email_body_text = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    email_body_text = part.get_payload(decode=True).decode()
                elif part.get_content_type() == "text/html":
                    email_body_text = part.get_payload(decode=True).decode()
        else:
            email_body_text = email_message.get_payload(decode=True).decode()
        
        print(f"\n📄 EMAIL BODY (Full):")
        print(f"{'='*70}")
        print(email_body_text)  # Print complete email body
        print(f"{'='*70}\n")
        
        # Extract download links from HTML
        import re
        download_links = re.findall(r'href=["\']([^"\'>]+)["\']', email_body_text)
        if download_links:
            print(f"\n🔗 FOUND DOWNLOAD LINKS:")
            for idx, link in enumerate(download_links, 1):
                if 'http' in link or 'download' in link.lower():
                    print(f"{idx}. {link}")
            print(f"{'='*70}\n")

        attachment_found = False
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))

                # 4. If an attachment is found
                if "attachment" in content_disposition or part.get_filename():
                    filename = part.get_filename()
                    if filename:
                        attachment_found = True
                        
                        # Decode filename
                        decoded = decode_header(filename)[0]
                        if decoded[1]: filename = decoded[0].decode(decoded[1])
                        elif isinstance(decoded[0], bytes): filename = decoded[0].decode()
                        else: filename = decoded[0]
                        
                        file_data = part.get_payload(decode=True)
                        file_size = len(file_data)
                        
                        print(f"📎 ATTACHMENT: {filename} ({file_size/1024:.2f} KB)")
                        
                        # Save attachment
                        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
                        filepath = os.path.join(DOWNLOAD_PATH, filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        
                        print(f"💾 Saved to: {filepath}")
                        
                        # Display file contents (for common text/report files)
                        if filename.lower().endswith(('.txt', '.csv', '.json', '.log', '.xml')):
                            try:
                                content = file_data.decode('utf-8')
                            except UnicodeDecodeError:
                                content = file_data.decode('latin-1', errors='ignore')
                            
                            print(f"\n📄 FILE CONTENTS:")
                            print(f"{'='*70}")
                            # Print contents, truncated for safety/cleanliness
                            lines = content.split('\n')
                            if len(lines) > 50:
                                print('\n'.join(lines[:50]))
                                print(f"... (Content truncated: {len(lines) - 50} more lines)")
                            else:
                                print(content)
                            print(f"{'='*70}")
                        
                        # NOTE: If you need to stop processing after the first attachment, uncomment 'break'
                        # break 
                        
            if not attachment_found:
                print("⚠️ No attachment found in this email.")
            else:
                # 5. Mark the processed email as SEEN (optional, comment out if you want to re-process it)
                mail.store(latest_email_id, '+FLAGS', '\Seen')
                print("✅ Email marked as SEEN (read).")
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP Error: {e}")
        print("💡 Check your Gmail App Password and ensure IMAP is enabled in your Gmail settings.")
    except Exception as e:
        print(f"\n❌ General Error: {e}")
    finally:
        try:
            if 'mail' in locals() and mail:
                mail.close()
                mail.logout()
                print("\n🔌 Disconnected from Gmail.")
        except Exception:
            pass

if __name__ == "__main__":
    if "jpyc uyqb eete gwxy" in EMAIL_PASSWORD:
        print("\n" + "="*70)
        print("⚠️  CRITICAL SETUP REQUIRED")
        print("="*70)
        print("Please replace the default EMAIL_PASSWORD with your 16-character Gmail App Password.")
        print("="*70 + "\n")
        sys.exit(1)
        
    search_and_download_report()