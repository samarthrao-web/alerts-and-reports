# api_handler.py
import requests
import json

# Updated for Internal Staging Environment
COMMON_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://euler-x.internal.staging.mum.juspay.net',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://euler-x.internal.staging.mum.juspay.net/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-device-type': 'web',
    'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
    'x-web-logintoken': '226d5f88e7a4142b98897799adbe3b'  # Token from staging CURL
}

COMMON_COOKIES = {
    '_clck': '1fel1nd%5E2%5Eg0j%5E0%5E2070',
    'mp_d1ddfec6b54b8f1475df460831368898_mixpanel': '%7B%22distinct_id%22%3A%20%221990aab6afd32cc-083efa789479e38-16525636-1d73c0-1990aab6afe37af%22%2C%22%24device_id%22%3A%20%221990aab6afd32cc-083efa789479e38-16525636-1d73c0-1990aab6afe37af%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Feuler-x.internal.svc.k8s.mum.juspay.net%2F%22%2C%22%24initial_referring_domain%22%3A%20%22euler-x.internal.svc.k8s.mum.juspay.net%22%7D',
    'X-Device-Id': 'Webb64cef85e4c644f2ae0995d990497384',
    'g_state': '{"i_l":0,"i_ll":1766050881673}',
    'token': '226d5f88e7a4142b98897799adbe3b'
}


def create_monitoring_task(url, report_config):
    """
    Sets the task name based on the API URL and executes the request for Internal Staging.
    """
    suffix = "NEW" if "reporting/task" in url else "OLD"

    payload = {
        "task_type": "report",
        "user": "juspay_sandbox_SAMARTH_RAO",  # Updated User
        "task_channel": ["mail"],
        "task_name": f"{report_config['task_name']} {suffix}",
        "task_description": report_config['task_description'],
        "mail": report_config['mail'],
        "start_timestamp": "2025-11-30T18:30:00.000Z",
        "end_timestamp": "2025-12-02T18:29:59.000Z",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata",
        "merchantId": "icicipru",  # Updated MerchantId
        "standard_report_type": report_config['standard_report_type']
    }

    print(f"\n🚀 STAGING REQUEST: {payload['task_name']}")
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
            print(f"Error Body: {response.text}")
            return None, None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None
