import imaplib
import email
from email.header import decode_header
import os
import re
import requests
import json

# --- CONFIGURATION ---
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "jpycuyqbeetegwxy"
SUBJECT_KEYWORD = "oldapi4"  # Change this to your email title
DOWNLOAD_DIR = "juspay_reports"
REPORT_PASSWORD = "juspay"  # Password for the report

def extract_report_id_from_url(url):
    """Extract report ID from download URL"""
    # Extract the report ID from URLs like:
    # https://sandbox.portal.juspay.in/download-report/b36a4a77-3bb1-4a2a-bb45-2a52aa52-63901554
    match = re.search(r'download-report/([^/?]+)', url)
    if match:
        return match.group(1)
    return None

def verify_password_and_download(report_id, save_dir):
    """Verify password and download the report"""
    try:
        print(f"🔐 Verifying password for report ID: {report_id}")
        
        # API endpoint for password verification
        api_url = f"https://sandbox.portal.juspay.in/api/monitoring/passwordMatch/{report_id}"
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://sandbox.portal.juspay.in',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://sandbox.portal.juspay.in/',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-device-type': 'web'
        }
        
        cookies = {
            '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
            'mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel': '%7B%22distinct_id%22%3A%20%2219831e26%22%2C%22%24device_id%22%3A%20%2219831e26%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D',
            '_hjSession_3095187': 'eyJpZCI6ImVlNjMzYjVlLWI3MjUtNDhmNS1hMTk0LTk4MzA0NWZhMTY2NyIsImMiOjE3NjU4NjQxMzIxMDMsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
        }
        
        # Verify password
        data = {"password": REPORT_PASSWORD}
        response = requests.post(api_url, headers=headers, cookies=cookies, json=data)
        
        print(f"📊 Password verification status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Password verified successfully")
            
            # Parse the response to get signed_url
            try:
                response_data = response.json()
                if 'signed_url' in response_data:
                    signed_url = response_data['signed_url']
                    print(f"\n🔗 SIGNED URL: {signed_url}")
                    download_url = signed_url
                else:
                    print("⚠️ No signed_url found in response")
                    download_url = f"https://sandbox.portal.juspay.in/download-report/{report_id}"
            except:
                print("⚠️ Could not parse JSON response")
                download_url = f"https://sandbox.portal.juspay.in/download-report/{report_id}"
            download_response = requests.get(download_url, headers=headers, cookies=cookies, allow_redirects=True)
            
            print(f"📊 Download response status: {download_response.status_code}")
            print(f"📊 Content-Type: {download_response.headers.get('Content-Type', 'unknown')}")
            print(f"📊 Content-Length: {len(download_response.content)} bytes")
            
            # Check first 200 characters to see what we got
            preview = download_response.content[:200]
            try:
                preview_text = preview.decode('utf-8', errors='ignore')
                print(f"📊 Response preview: {preview_text}")
            except:
                print(f"📊 Response preview (raw): {preview}")
            
            if download_response.status_code == 200:
                # Save the CSV file
                os.makedirs(save_dir, exist_ok=True)
                filename = f"report_{report_id}.csv"
                filepath = os.path.join(save_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(download_response.content)
                
                print(f"✅ Downloaded: {filepath} ({len(download_response.content)/1024:.2f} KB)")
                
                return filepath
            else:
                print(f"❌ Download failed: Status {download_response.status_code}")
                print(f"Content-Type: {download_response.headers.get('Content-Type', 'unknown')}")
        else:
            print(f"❌ Password verification failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def extract_download_link(html_content):
    """Extract download link from HTML email"""
    # Clean up HTML content
    html_content = html_content.replace('#commit ', '').replace('commit ', '')
    
    # Find download-report URLs
    urls = re.findall(r'https?://[^\s"\'<>]+', html_content)
    
    print("\n🔗 ALL URLS FOUND:")
    for url in urls:
        print(" ", url)
    
    for url in urls:
        if 'download-report' in url:
            return url
    
    return None

def main():
    print(f"\n{'='*70}")
    print("📧 Email Report Downloader with Password Protection")
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
        
        # Extract download link
        download_link = extract_download_link(html_body)
        
        if download_link:
            print(f"🔗 Found download link: {download_link}")
            report_id = extract_report_id_from_url(download_link)
            
            if report_id:
                verify_password_and_download(report_id, DOWNLOAD_DIR)
            else:
                print("❌ Could not extract report ID from download link")
        else:
            print("❌ No download link found in email")
        
        mail.close()
        mail.logout()
        print("\n🔌 Disconnected from Gmail")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()