import requests
import json
from Transaction_dimension import transaction_dim1

def create_reporting_task(dimensions_list):
    url = 'https://euler-x.internal.staging.mum.juspay.net/reporting/task'

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://euler-x.internal.staging.mum.juspay.net',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://euler-x.internal.staging.mum.juspay.net/',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-device-type': 'web',
        'x-feature': 'canary',
        'x-tenant-id': 'jt_29bd8266cbdc4e76938cfaa2d80db4d6',
        'x-web-logintoken': '5ef591176df420c9635788684125ec',
        'Cookie': '_clck=1fel1nd%5E2%5Eg0j%5E0%5E5E2070; mp_d1ddfec6b54b8f1475df460831368898_mixpanel=%7B%22distinct_id%22%3A%20%221990aa-083efa78-16525636-1d73c0-1990aab6%22%2C%22%24device_id%22%3A%20%221990aa-083efa78-16525636-1d73c0-1990aab6%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Feuler-x.internal.svc.k8s.mum.juspay.net%2F%22%2C%22%24initial_referring_domain%22%3A%20%22euler-x.internal.svc.k8s.mum.juspay.net%22%7D; X-Device-Id=Webb64cef85e4c644f2ae0995d990497384; g_state={"i_l":0,"i_ll":17655162}; token=d7bd3da0'
    }

    data = {
        "task_type": "report",
        "user": "juspay_sandbox_SAMARTH_RAO",
        "interval": 86400,
        "filters": {
            "payment_method_type": [
                "CARD",
                "UPI",
                "NB"
            ],
            "txn_latency_enum": [
                "3M-4M"
            ],
            "udf6": [
                None
            ]
        },
        "source": "txn",
        "dimensions": dimensions_list,
        "query_duration": 2592000,
        "metrics": [
            "success_rate",
            "total_volume",
            "success_volume",
            "total_amount"
        ],
        "merchantId": "juspay",
        "task_channel": [
            "mail"
        ],
        "task_name": "newapi1",
        "task_description": "testing new api",
        "mail": [
            "samarth.rao@juspay.in"
        ],
        "schedule_time": "8:45",
        "schedule_day_date": "",
        "timezone_offset": 330,
        "timezone_region": "Asia/Kolkata"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        print("\\nRequest Successful!")
        print("Status Code:", response.status_code)

        try:
            print("Response JSON:", response.json())
        except json.JSONDecodeError:
            print("Response Text:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        try:
            print("Error JSON:", http_err.response.json())
        except:
            print("Error Response:", http_err.response.text)
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)

if __name__ == "__main__":
    create_reporting_task(transaction_dim)