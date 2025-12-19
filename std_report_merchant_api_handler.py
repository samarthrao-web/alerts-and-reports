import requests
import json

# Headers and Cookies remain as per your latest working Sandbox curl
COMMON_HEADERS = {
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
    'x-device-type': 'web',
    'x-feature': 'canary',
    'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
    'x-web-logintoken': '85c1197ebda48678d85257ab09a008'
}

COMMON_COOKIES = {
    '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
    '_clck': '1szir1k%5E2%5Eg1o%5E0%5E2029',
    'g_state': '{"i_l":0,"i_ll":1766052667133,"i_b":"fJTyR3EaQaiO/we3R/NGhCPpheOqCpfoZF7PaeVaEZ0","i_e":{"enable_itp_optimization":0}}',
    '_hjSession_3095187': 'eyJpZCI6Ijg5NzUzYWY1LTJmZDgtNDVlZi04ZGMyLTViOWU0YmM3OTFkMyIsImMiOjE3NjYwNTA5MDg4NDUsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
}


def create_monitoring_task(url, report_config):
    """
    Executes request and returns a dictionary of data extracted from response.
    """
    suffix = "NEW" if "reporting/task" in url else "OLD"
    final_task_name = f"{report_config['task_name']} {suffix}"

    payload = {
        "task_type": "report",
        "user": "chetan_test_samarth_rao",
        "task_channel": ["mail"],
        "task_name": final_task_name,
        "task_description": report_config['task_description'],
        "mail": report_config['mail'],
        "start_timestamp": "2025-08-01T18:30:00.000Z",
        "end_timestamp": "2025-12-02T18:29:59.000Z",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata",
        "merchantId": "chetan_test",
        "standard_report_type": report_config['standard_report_type']
    }

    try:
        response = requests.post(
            url, headers=COMMON_HEADERS, cookies=COMMON_COOKIES, data=json.dumps(payload), timeout=30)

        if response.status_code == 200:
            resp_data = response.json()
            print(f"✅ Success! {final_task_name}")
            return {
                "task_name": final_task_name,
                "job_id": resp_data.get('job_id'),
                "task_id": resp_data.get('task_uid')  # task_uid
            }
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
