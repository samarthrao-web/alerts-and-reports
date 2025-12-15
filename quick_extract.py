import imaplib
import email
from email.header import decode_header
import os

# Gmail Configuration
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "jpycuyqbeetegwxy"  # You'll need to add your Gmail App Password here

# Search for this specific email
SUBJECT_KEYWORD = "[JUSPAY] Daily Report - oldapi2"

def extract_and_print_report():
    """Extract and print the JUSPAY Daily Report."""
    
    print(f"\n{'='*70}")
    print("📧 Connecting to Gmail...")
    print(f"{'='*70}\n")
    
    # Connect to Gmail
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("✅ Successfully connected to Gmail\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\n💡 Make sure you:")
        print("   1. Enable 2-Step Verification in Google Account")
        print("   2. Generate App Password: https://myaccount.google.com/apppasswords")
        print("   3. Add the 16-character App Password to this script")
        return
    
    try:
        # Select inbox
        mail.select("inbox")
        
        # Search for the specific email
        print(f"🔍 Searching for: '{SUBJECT_KEYWORD}'")
        status, messages = mail.search(None, f'SUBJECT "{SUBJECT_KEYWORD}"')
        
        if status != "OK":
            print("❌ Search failed")
            return
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print("❌ No emails found with that subject")
            print("\n💡 Try searching manually in Gmail to verify the exact subject line")
            return
        
        print(f"✅ Found {len(email_ids)} email(s)\n")
        
        # Get the most recent email (last in the list)
        latest_email_id = email_ids[-1]
        
        # Fetch the email
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        
        if status != "OK":
            print("❌ Failed to fetch email")
            return
        
        # Parse email
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        # Get email details
        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        
        from_email = email_message.get("From")
        date = email_message.get("Date")
        
        print(f"{'='*70}")
        print(f"📨 EMAIL DETAILS")
        print(f"{'='*70}")
        print(f"Subject: {subject}")
        print(f"From: {from_email}")
        print(f"Date: {date}")
        print(f"{'='*70}\n")
        
        # Extract and print email content
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Print text body
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        print(f"{'='*70}")
                        print(f"📄 EMAIL BODY (TEXT)")
                        print(f"{'='*70}")
                        print(body)
                        print(f"{'='*70}\n")
                    except:
                        pass
                
                # Print HTML body (converted to readable format)
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        html_body = part.get_payload(decode=True).decode()
                        print(f"{'='*70}")
                        print(f"📄 EMAIL BODY (HTML)")
                        print(f"{'='*70}")
                        # Print first 1000 characters of HTML
                        print(html_body[:1000])
                        if len(html_body) > 1000:
                            print(f"\n... (truncated, total length: {len(html_body)} characters)")
                        print(f"{'='*70}\n")
                    except:
                        pass
                
                # Handle attachments
                elif "attachment" in content_disposition or part.get_filename():
                    filename = part.get_filename()
                    if filename:
                        # Decode filename
                        decoded = decode_header(filename)[0]
                        if decoded[1]:
                            filename = decoded[0].decode(decoded[1])
                        elif isinstance(decoded[0], bytes):
                            filename = decoded[0].decode()
                        else:
                            filename = decoded[0]
                        
                        file_data = part.get_payload(decode=True)
                        file_size = len(file_data)
                        
                        print(f"{'='*70}")
                        print(f"📎 ATTACHMENT: {filename}")
                        print(f"{'='*70}")
                        print(f"Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
                        
                        # Save attachment
                        os.makedirs("downloaded_reports", exist_ok=True)
                        filepath = os.path.join("downloaded_reports", filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        
                        print(f"💾 Saved to: {filepath}")
                        
                        # If it's a text file (CSV, TXT, JSON), print contents
                        if filename.endswith(('.txt', '.csv', '.json', '.log')):
                            try:
                                content = file_data.decode('utf-8')
                                print(f"\n📄 FILE CONTENTS:")
                                print(f"{'-'*70}")
                                print(content)
                                print(f"{'-'*70}")
                            except:
                                print("(Binary file - cannot display as text)")
                        
                        print(f"{'='*70}\n")
        else:
            # Non-multipart email
            try:
                body = email_message.get_payload(decode=True).decode()
                print(f"{'='*70}")
                print(f"📄 EMAIL BODY")
                print(f"{'='*70}")
                print(body)
                print(f"{'='*70}\n")
            except:
                print("❌ Could not decode email body")
        
        print(f"{'='*70}")
        print("✅ Email extraction complete!")
        print(f"{'='*70}\n")
        
    finally:
        mail.close()
        mail.logout()
        print("🔌 Disconnected from Gmail")

if __name__ == "__main__":
    if not EMAIL_PASSWORD:
        print("\n" + "="*70)
        print("⚠️  SETUP REQUIRED")
        print("="*70)
        print("\nPlease follow these steps:")
        print("\n1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Sign in to your Google Account (samarth.rao@juspay.in)")
        print("3. Enable 2-Step Verification if not already enabled")
        print("4. Create a new App Password:")
        print("   - Select app: Mail")
        print("   - Select device: Other (Custom name)")
        print("   - Name it: 'Python Email Extractor'")
        print("5. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')")
        print("6. Edit this file (quick_extract.py) and paste it in EMAIL_PASSWORD")
        print("\nExample:")
        print('   EMAIL_PASSWORD = "abcdefghijklmnop"  # Remove spaces')
        print("\n" + "="*70 + "\n")
    else:
        extract_and_print_report()