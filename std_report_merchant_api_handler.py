# api_handler.py
import requests
import json

COMMON_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://sandbox.portal.juspay.in',
    'pragma': 'no-cache',
    'referer': 'https://sandbox.portal.juspay.in/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-device-type': 'web',
    'x-feature': 'canary',
    'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
    'x-web-logintoken': '7a7e3fdfc8543b8bf7faf4cdedd16b'
}

COMMON_COOKIES = {
    '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSessionUser_5094217': 'eyJpZCI6IjU0MGIyYjM5LTAyMTMtNTY3Yy04MWY2LWI4ZDcxMjUyZTkxNCIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc1MzcsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSessionUser_3119518': 'eyJpZCI6Ijk5ZGYwZDRlLTQ3MjktNTU4ZS05NmZiLTI4YWZlYmYzNzNkNyIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc4NDQsImV4aXN0aW5nIjp0cnVlfQ==',
    'mp_d1ddfec6b54b8f1475df460831368898_mixpanel': '%7B%22distinct_id%22%3A%20%2219888a01c20279c-0a31f6359f1dbd-17525636-1d73c0-19888a01c213c2c%22%2C%22%24device_id%22%3A%20%2219888a01c20279c-0a31f6359f1dbd-17525636-1d73c0-19888a01c213c2c%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fportal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22portal.juspay.in%22%7D',
    '_clck': '1szir1k%5E2%5Eg1o%5E0%5E2029',
    'mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel': '%7B%22distinct_id%22%3A%20%2219831e2697a2c28-028816eb8725d88-17525636-1d73c0-19831e2697b3b34%22%2C%22%24device_id%22%3A%20%2219831e2697a2c28-028816eb8725d88-17525636-1d73c0-19831e2697b3b34%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D',
    '_hjSession_3095187': 'eyJpZCI6IjYxNTVjZDBhLWE3ODMtNDBmZC04ZDUwLTJhZmE3MWVhODZiNyIsImMiOjE3NjYwMzAzOTUxMjksInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=',
    'g_state': '{"i_l":0,"i_ll":1766035090629,"i_b":"Hr4LQfBRtlxeAz4pYpz7Ah12+5DAxfHP5p4aCBQaoWs","i_e":{"enable_itp_optimization":0}}'
}


def create_monitoring_task(url, report_config):
    """
    Sets the task name based on the API URL and executes the request.
    """
    # Logic to add suffix based on URL
    if "reporting/task" in url:
        suffix = "NEW"
    else:
        suffix = "OLD"

    payload = {
        "task_type": "report",
        "user": "chetan_test_samarth_rao",
        "task_channel": ["mail"],
        # Dynamics suffix added here
        "task_name": f"{report_config['task_name']} {suffix}",
        "task_description": report_config['task_description'],
        "mail": report_config['mail'],
        "start_timestamp": "2025-07-01T18:30:00.000Z",
        "end_timestamp": "2025-12-02T18:29:59.000Z",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata",
        "merchantId": "chetan_test",
        "standard_report_type": report_config['standard_report_type']
    }

    print(f"\n🚀 PREPARING REQUEST: {payload['task_name']}")
    print(f"📦 URL: {url}")

    try:
        response = requests.post(
            url,
            headers=COMMON_HEADERS,
            cookies=COMMON_COOKIES,
            data=json.dumps(payload),
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id') or data.get('task_id')
            print(f"✅ Success! Job ID: {job_id}")
            return response.headers.get('x-response-id'), job_id
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"Error: {response.text}")
            return None, None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None
