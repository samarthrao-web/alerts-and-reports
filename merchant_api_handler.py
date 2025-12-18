# api_handler.py

import requests
import json
from datetime import datetime, timedelta

# --- COMMON CONSTANTS ---

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
    'x-web-logintoken': '1a1a5177e93470b8a385cc1f44f3ba'    # Merchant token 
}

COMMON_COOKIES = {
    '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSessionUser_5094217': 'eyJpZCI6IjU0MGIyYjM5LTAyMTMtNTY3Yy04MWY2LWI4ZDcxMjUyZTkxNCIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc1MzcsImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjSessionUser_3119518': 'eyJpZCI6Ijk5ZGYwZDRlLTQ3MjktNTU4ZS05NmZiLTI4YWZlYmYzNzNkNyIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc4NDQsImV4aXN0aW5nIjp0cnVlfQ==',
    'mp_d1ddfec6b54b8f1475df460831368898_mixpanel': '%7B%22distinct_id%22%3A%20%2219888a01%22%2C%22%24device_id%22%3A%20%2219888a01%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fportal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22portal.juspay.in%22%7D',
    '_clck': '1szir1k%5E2%5Eg1o%5E0%5E2029',
    'mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel': '%7B%22distinct_id%22%3A%20%2219831e26%22%2C%22%24device_id%22%3A%20%2219831e26%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D',
    'g_state': '{"i_l":0,"i_ll":17657933,"i_b":"IM/KORyIgIgHrnYoPolj+M89bnalUhNW1edKx3mk6Tk","i_e":{"enable_itp_optimization":0}}',
    '_hjSession_3095187': 'eyJpZCI6ImVmM2VmZjU2LTNkMmYtNGQ5Ny05MDJjLTc4MjAzMGIxNzQzMiIsImMiOjE3NjU3OTM0MjgwMzcsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
}

BASE_DATA = {
    "task_type": "report",
    "user": "chetan_test_samarth_rao",
    "interval": 86400,
    "source": "txn",
    # "dimensions" set later
    "metrics": ["success_rate"],
    "merchantId": "chetan_test",
    "task_channel": ["mail"],
    "output_format": "csv",
    # "task_name" set later
    "task_description": "testing",
    "mail": ["samarth.rao@juspay.in"],
    "schedule_time": "10:50",
    "schedule_day_date": "",
    "timezone_offset": 330,
    "timezone_region": "Asia/Kolkata"
}
# --- END COMMON CONSTANTS ---


def create_monitoring_task(url, dimensions_list, dim_name, task_name):
    """
    Executes a single API call, returns x-response-id and the job/task ID from JSON.
    """
    
    # Create a copy of the base payload and update the dynamic fields
    data = BASE_DATA.copy()
    data["dimensions"] = dimensions_list
    data["task_name"] = task_name

    x_response_id = "N/A"
    job_id = None

    try:
        print(f"\n{'='*60}")
        print(f"Executing API call for {dim_name} at URL: {url}")
        print(f"{'='*60}")
        # print("\nRequest Payload:") # Commented out to reduce console clutter
        # print(json.dumps(data, indent=2))
        
        response = requests.post(url, headers=COMMON_HEADERS, cookies=COMMON_COOKIES, json=data, timeout=30)
        response.raise_for_status()

        x_response_id = response.headers.get('x-response-id', 'Not found')
        print(f"\n✅ Request Successful! Status Code: {response.status_code}")
        print("x-response-id:", x_response_id)
        
        try:
            response_data = response.json()
            # ASSUMPTION: The unique ID is stored under the key 'job_id' or 'task_id'.
            # *** UPDATE THIS KEY IF NECESSARY ***
            job_id = response_data.get('job_id') or response_data.get('task_id')
            
            if job_id:
                 print(f"Extracted Job/Task ID: {job_id}")
            else:
                 print("Warning: Job/Task ID not found in JSON response.")
            
        except json.JSONDecodeError:
            print("Warning: Response was not valid JSON.")
            pass # Keep job_id as None
        
        return x_response_id, job_id

    except requests.exceptions.HTTPError as http_err:
        if http_err.response is not None:
            x_response_id = http_err.response.headers.get('x-response-id', 'Not found')
            print(f"\n❌ HTTP error occurred: {http_err}")
            print("x-response-id:", x_response_id)
            try:
                print("Error JSON:", http_err.response.json())
            except:
                print("Error Response:", http_err.response.text)
        return x_response_id, None
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Exception: {e}")
        return None, None