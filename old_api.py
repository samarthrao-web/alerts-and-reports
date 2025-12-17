import requests
import json
from datetime import datetime, timedelta
from Transaction_dimension import transaction_dim1 #, transaction_dim2, transaction_dim3, transaction_dim4

def create_monitoring_task(dimensions_list, dim_name):

    url = 'https://sandbox.portal.juspay.in/api/monitoring/task'

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
        'x-web-logintoken': '94d786ba8ec4011b696a0cd0dbd162'    # this has to be done dynamic , Merchant token 
    }

    cookies = {
        '_hjSessionUser_3095187': 'eyJpZCI6ImY1MjU3ZDU3LTk1MTktNTFlOS04MDVlLTMzNGZhNzljODI0ZSIsImNyZWF0ZWQiOjE3NTMxNjc3MTM0MTIsImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjSessionUser_5094217': 'eyJpZCI6IjU0MGIyYjM5LTAyMTMtNTY3Yy04MWY2LWI4ZDcxMjUyZTkxNCIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc1MzcsImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjSessionUser_3119518': 'eyJpZCI6Ijk5ZGYwZDRlLTQ3MjktNTU4ZS05NmZiLTI4YWZlYmYzNzNkNyIsImNyZWF0ZWQiOjE3NTQ0Njg2MDc4NDQsImV4aXN0aW5nIjp0cnVlfQ==',
        'mp_d1ddfec6b54b8f1475df460831368898_mixpanel': '%7B%22distinct_id%22%3A%20%2219888a01%22%2C%22%24device_id%22%3A%20%2219888a01%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fportal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22portal.juspay.in%22%7D',
        '_clck': '1szir1k%5E2%5Eg1o%5E0%5E2029',
        'mp_efd8be2f877ffef30849e90a2ad99b37_mixpanel': '%7B%22distinct_id%22%3A%20%2219831e26%22%2C%22%24device_id%22%3A%20%2219831e26%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fsandbox.portal.juspay.in%2F%22%2C%22%24initial_referring_domain%22%3A%20%22sandbox.portal.juspay.in%22%7D',
        'g_state': '{"i_l":0,"i_ll":17657933,"i_b":"IM/KORyIgIgHrnYoPolj+M89bnalUhNW1edKx3mk6Tk","i_e":{"enable_itp_optimization":0}}',
        '_hjSession_3095187': 'eyJpZCI6ImVmM2VmZjU2LTNkMmYtNGQ5Ny05MDJjLTc4MjAzMGIxNzQzMiIsImMiOjE3NjU3OTM0MjgwMzcsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0='
    }

    data = {
        "task_type": "report",
        "user": "chetan_test_samarth_rao",
        "interval": 86400,
        "source": "txn",
        "dimensions": dimensions_list,
        "metrics": ["success_rate"],
        "merchantId": "chetan_test",
        "task_channel": ["mail"],
        "output_format": "csv",
        "task_name": "testing old api 1",
        "task_description": "testing",
        "mail": ["samarth.rao@juspay.in"],
        "schedule_time": "09:50",
        "schedule_day_date": "",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata"
    }

    try:
        print(f"\n{'='*60}")
        print(f"Executing API call for {dim_name}")
        print(f"{'='*60}")
        print("\nRequest Payload:")
        print(json.dumps(data, indent=2))
        
        response = requests.post(url, headers=headers, cookies=cookies, json=data, timeout=30)
        response.raise_for_status()

        print("\n✅ Request Successful!")
        print("Status Code:", response.status_code)
        
        # Display scheduled time in IST
        utc_time = data["schedule_time"]
        utc_hour, utc_minute = map(int, utc_time.split(":"))
        utc_datetime = datetime.now().replace(hour=utc_hour, minute=utc_minute, second=0, microsecond=0)
        ist_datetime = utc_datetime + timedelta(hours=5, minutes=30)
        ist_time = ist_datetime.strftime("%I:%M %p")
        print(f"Scheduled Time (IST): {ist_time}")
        
        # Display x-response-id header
        if 'x-response-id' in response.headers:
            print("x-response-id:", response.headers['x-response-id'])
        else:
            print("x-response-id: Not found in response headers")

        try:
            print("Response JSON:", response.json())
        except json.JSONDecodeError:
            print("Response Text:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
        
        # Display x-response-id header for errors
        if 'x-response-id' in http_err.response.headers:
            print("x-response-id:", http_err.response.headers['x-response-id'])
        else:
            print("x-response-id: Not found in error response headers")
        
        try:
            print("Error JSON:", http_err.response.json())
        except:
            print("Error Response:", http_err.response.text)
    except requests.exceptions.RequestException as e:
        print("❌ Request Exception:", e)

if __name__ == "__main__":
    # Collect all transaction dimensions
    all_transaction_dims = [
        (transaction_dim1, "transaction_dim1"),
        # (transaction_dim2, "transaction_dim2"),
        # (transaction_dim3, "transaction_dim3"),
        # (transaction_dim4, "transaction_dim4")
    ]
    
    # Execute API call for each transaction dimension
    for dim_list, dim_name in all_transaction_dims:
        create_monitoring_task(dim_list, dim_name)
    
    print(f"\n{'='*60}")
    print("✅ All API calls completed!")
    print(f"{'='*60}")