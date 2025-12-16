import imaplib
import email
from email.header import decode_header
import os
import re
import requests

# ---------------- CONFIG ----------------
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "samarth.rao@juspay.in"
EMAIL_PASSWORD = "jpycuyqbeetegwxy"
SUBJECT_KEYWORD = "oldapi4"
DOWNLOAD_DIR = "juspay_reports"
# --------------------------------------


def extract_any_download_link(content):
    """
    Extract ANY reasonable download/report URL
    from HTML or plain text.
    """
    urls = re.findall(r'https?://[^\s"\'>]+', content, re.I)

    print("\n🔗 ALL URLS FOUND:")
    for u in urls:
        print(" ", u)

    for url in urls:
        lowered = url.lower()
        if any(k in lowered for k in ["download", "report", "export", "csv"]):
            return url

    return urls[0] if urls else None


def download_file(url, save_dir):
    try:
        print(f"\n⬇️  Downloading: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        }

        response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()

        ct = response.headers.get("Content-Type", "")
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Content-Type: {ct}")

        if "text/html" in ct.lower():
            print("❌ HTML received instead of file (login required)")
            return None

        filename = "report.csv"
        cd = response.headers.get("Content-Disposition", "")
        match = re.search(r'filename="?([^"]+)"?', cd)
        if match:
            filename = match.group(1)

        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, filename)

        with open(path, "wb") as f:
            f.write(response.content)

        print(f"✅ Saved: {path}")

        try:
            print("\n📄 FILE CONTENT:")
            print("=" * 60)
            print(response.content.decode("utf-8")[:2000])
            print("=" * 60)
        except Exception:
            print("⚠️ Binary file")

        return path

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def main():
    print("\n📧 Email Report Downloader\n")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, f'(TEXT "{SUBJECT_KEYWORD}")')
    if status != "OK" or not messages[0]:
        print("❌ No matching emails found")
        return

    latest_id = messages[0].split()[-1]
    _, msg_data = mail.fetch(latest_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])

    subject, enc = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(enc or "utf-8")
    print(f"📨 Subject: {subject}")

    full_content = ""

    print("\n📦 MIME PARTS FOUND:")
    for part in msg.walk():
        ctype = part.get_content_type()
        disp = part.get("Content-Disposition", "")
        print(" ", ctype, disp)

        # ✅ Attachment or inline file
        if part.get_filename():
            filename = part.get_filename()
            data = part.get_payload(decode=True)

            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            path = os.path.join(DOWNLOAD_DIR, filename)

            with open(path, "wb") as f:
                f.write(data)

            print(f"✅ Attachment saved: {path}")
            return

        # Collect body content
        if ctype in ("text/html", "text/plain"):
            payload = part.get_payload(decode=True)
            if payload:
                full_content += payload.decode(errors="ignore")

    print("\n📄 EMAIL BODY (first 1500 chars):")
    print(full_content[:1500])

    # ✅ Extract link
    link = extract_any_download_link(full_content)

    if not link:
        print("❌ No downloadable link found")
        return

    print(f"\n🎯 Selected download link:\n{link}")
    download_file(link, DOWNLOAD_DIR)

    mail.close()
    mail.logout()
    print("\n🔌 Disconnected")


if __name__ == "__main__":
    main()
