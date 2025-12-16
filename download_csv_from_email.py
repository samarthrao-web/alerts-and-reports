import imaplib
import email
from email.header import decode_header
import os
import re
import requests

# --- CONFIGURATION ---
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "jpycuyqbeetegwxy"
SUBJECT_KEYWORD = "testing old api 1"
DOWNLOAD_DIR = "juspay_reports"

def extract_download_link(html_content):
    """Extract the download report link from HTML email."""
    # Remove #commit markers that might be in the HTML
    html_content = html_content.replace('#commit ', '#')
    
    # Search for download-report link
    match = re.search(r'href=\s*["\']([^"\']*download-report[^"\']*)["\']', html_content, re.IGNORECASE)
    if match:
        link = match.group(1)
        # Clean up any remaining #commit markers
        link = link.replace('#commit', '').replace('commit ', '')
        return link
    return None

def download_csv_from_link(url, save_dir):
    """Download CSV file from the given URL."""
    try:
        print(f"🔗 Downloading from: {url}")
        
        # Authentication headers and cookies from old_api.py
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-device-type': 'web',
            'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
            'x-web-logintoken': '5ef591176df420c9635788684125ec'
        }
        
        cookies = {
            '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
            'mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel': '%7B%22distinct_id%22%3A%20%2219831e26%22%2C%22%24device_id%22%3A%20%2219831e26%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D',
            '_hjSession_3095187': 'eyJpZCI6ImVmM2VmZjU2LTNkMmYtNGQ5Ny05MDJjLTc4MjAzMGIxNzQzMiIsImMiOjE3NjU3OTM0MjgwMzcsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
        }
        
        response = requests.get(url, headers=headers, cookies=cookies, allow_redirects=True)
        response.raise_for_status()
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"📊 Content-Length: {len(response.content)} bytes")
        
        # Check if we got HTML (login page) instead of CSV
        if 'text/html' in response.headers.get('Content-Type', ''):
            print("⚠️  Received HTML instead of CSV - authentication may have failed")
            print("⚠️  Your login token may have expired")
            return None
        
        # Extract filename from Content-Disposition header or URL
        filename = "report.csv"
        if 'Content-Disposition' in response.headers:
            cd = response.headers['Content-Disposition']
            fname_match = re.findall('filename="?([^"]+)"?', cd)
            if fname_match:
                filename = fname_match[0]
        
        # Save file
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {filepath} ({len(response.content)/1024:.2f} KB)")
        
        # Display CSV content
        try:
            content = response.content.decode('utf-8')
            print(f"\n📄 CSV CONTENT:")
            print("="*70)
            print(content)
            print("="*70)
        except:
            print("⚠️ Could not display content (binary file)")
        
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def main():
    print(f"\n{'='*70}")
    print("📧 Email CSV Report Downloader")
    print(f"{'='*70}\n")
    
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("✅ Connected to Gmail")
        
        mail.select("inbox")
        
        # Search for emails
        search_criteria = f'(TEXT "{SUBJECT_KEYWORD}")'
        status, messages = mail.search(None, search_criteria)
        
        if status != "OK":
            print(f"❌ Search failed")
            return
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print(f"🔍 No emails found with subject '{SUBJECT_KEYWORD}'")
            return
        
        # Get only the latest email
        latest_id = email_ids[-1]
        print(f"✅ Processing latest email (found {len(email_ids)} total)...")
        status, msg_data = mail.fetch(latest_id, "(RFC822)")
        
        if status != "OK":
            print(f"❌ Failed to fetch email")
            return
        
        # Parse email
        email_message = email.message_from_bytes(msg_data[0][1])
        
        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        
        print(f"\n📨 Subject: {subject}")
        
        # Extract HTML body
        html_body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True).decode()
                    break
        else:
            html_body = email_message.get_payload(decode=True).decode()
        
        # First, check for direct attachments
        attachment_found = False
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition or part.get_filename():
                    filename = part.get_filename()
                    if filename:
                        attachment_found = True
                        decoded = decode_header(filename)[0]
                        if decoded[1]: filename = decoded[0].decode(decoded[1])
                        elif isinstance(decoded[0], bytes): filename = decoded[0].decode()
                        else: filename = decoded[0]
                        
                        file_data = part.get_payload(decode=True)
                        
                        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                        filepath = os.path.join(DOWNLOAD_DIR, filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        
                        print(f"✅ Downloaded attachment: {filepath} ({len(file_data)/1024:.2f} KB)")
                        
                        # Display CSV content
                        if filename.lower().endswith('.csv'):
                            try:
                                content = file_data.decode('utf-8')
                                print(f"\n📄 CSV CONTENT:")
                                print("="*70)
                                print(content)
                                print("="*70)
                            except:
                                print("⚠️ Could not display content")
        
        # If no attachment, try download link
        if not attachment_found:
            download_link = extract_download_link(html_body)
            if download_link:
                print(f"🔗 Found download link: {download_link}")
                download_csv_from_link(download_link, DOWNLOAD_DIR)
            else:
                print("❌ No attachment or download link found in email")
        
        mail.close()
        mail.logout()
        print("\n🔌 Disconnected from Gmail")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()