import requests
import json

def create_monitoring_task():
    """Create monitoring task using EXACT curl format."""
    
    # Exact URL from your working curl
    url = 'https://sandbox.portal.juspay.in/api/monitoring/task'
    
    # Exact headers from your working curl
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
        'x-device-type': 'web',
        'x-feature': 'canary',
        'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
        'x-web-logintoken': '5ef59117'
    }
    
    # Exact cookies from your working curl (as single string)
    cookies_string = '_hjSessionUser_3095187=eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_5094217=eyJpZCI6IjU0MGIyYjM5LTAyMTMtNTY3Yy04MWY2LWI4ZDcxMjUyZTkxNCIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc1MzcsImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_3119518=eyJpZCI6Ijk5ZGYwZDRlLTQ3MjktNTU4ZS05NmZiLTI4YWZlYmYzNzNkNyIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc4NDQsImV4aXN0aW5nIjp0cnVlfQ==; mp_d1ddfec6b54b8f1475df460831368898_mixpanel=%7B%22distinct_id%22%3A%20%2219888a01c20279c%22%2C%22%24device_id%22%3A%20%2219888a01c20279c%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fportal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22portal.juspay.in%22%7D; _clck=1szir1k%5E2%5Eg1o%5E0%5E2029; mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel=%7B%22distinct_id%22%3A%20%2219831e2697a2c28%22%2C%22%24device_id%22%3A%20%2219831e2697a2c28%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D; g_state={"i_l":0,"i_ll":17657933,"i_b":"IM/KORyIgIgHrnYoPolj+M89bnalUhNW1edKx3mk6Tk","i_e":{"enable_itp_optimization":0}}; _hjSession_3095187=eyJpZCI6ImVmM2VmZjU2LTNkMmYtNGQ5Ny05MDJjLTc4MjAzMGIxNzQzMiIsImMiOjE3NjU3OTM0MjgwMzcsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
    
    # Parse cookies into dict
    cookies = {}
    for cookie in cookies_string.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key] = value
    
    # EXACT data from your working curl (NO query_duration!)
    data = {
        "task_type": "report",
        "user": "chetan_test_samarth_rao",
        "interval": 86400,
        "source": "txn",
        "dimensions": [
            "payment_method_type",
            "txn_latency_enum"
        ],
        "metrics": [
            "success_rate"
        ],
        "merchantId": "chetan_test",
        "task_channel": [
            "mail"
        ],
        "task_name": "testingchange1",
        "task_description": "testing",
        "mail": [
            "samarth.rao@juspay.in"
        ],
        "schedule_time": "11:30",
        "schedule_day_date": "",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata"
    }
    
    try:
        print(f"\n{'='*70}")
        print("🧪 TESTING WITH EXACT CURL FORMAT")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"Method: POST")
        print(f"Headers: {len(headers)} headers")
        print(f"Cookies: {len(cookies)} cookies")
        print(f"\n📋 Request Data:")
        print(json.dumps(data, indent=2))
        
        # Make the request
        response = requests.post(
            url, 
            headers=headers, 
            cookies=cookies, 
            json=data, 
            timeout=30
        )
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        
        # Display x-response-id header
        if 'x-response-id' in response.headers:
            print(f"x-response-id: {response.headers['x-response-id']}")
        else:
            print("x-response-id: Not found")
        
        # Display response
        if response.status_code == 200:
            print(f"\n✅ SUCCESS!")
            try:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
            except:
                print(f"Response: {response.text}")
        else:
            print(f"\n❌ FAILED!")
            try:
                error_json = response.json()
                print(f"Error: {json.dumps(error_json, indent=2)}")
            except:
                print(f"Error: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = create_monitoring_task()
    
    print(f"\n{'='*70}")
    if success:
        print("✅ API CALL SUCCESSFUL!")
    else:
        print("❌ API CALL FAILED!")
    print(f"{'='*70}")