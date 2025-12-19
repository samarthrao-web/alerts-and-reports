# main_executor.py
from std_report_merchant_api_handler import create_monitoring_task
import json

OLD_API_URL = 'https://sandbox.portal.juspay.in/api/monitoring/task'
NEW_API_URL = 'https://sandbox.portal.juspay.in/reporting/task'

REPORTS_TO_EXECUTE = [
    {
        "task_name": "19 9 40 Transaction Refund Report",
        "task_description": "Comprehensive report representing previous day transactions and refunds data.",
        "mail": ["samarth.rao@juspay.in",
                 "rahul.jagdhane@juspay.in"],
        "standard_report_type": "TXN_REFUND"
    },
    {
        "task_name": "New Orders Report",
        "task_description": "This report provides details of orders with status as NEW. This is the status if order is created but transaction is not attempted on it",
        "mail": [
            "samarth.rao@juspay.in"
        ],
        "standard_report_type": "NEW_ORDERS"
    },
    {
        "task_name": "Payout Fulfillment Txn Report",
        "task_description": "A payout fulfillment report is a document or summary that provides information about various financial transactions or payments made by an organization to individuals, vendors, employees, or other entities.",
        "mail": [
            "samarth.rao@juspay.in"
        ],
        "standard_report_type": "PAYOUT_FULFILLMENT"
    },
]

monitoring_task_queue = []

if __name__ == "__main__":
    for report in REPORTS_TO_EXECUTE:
        # Get data from OLD API
        old_data = create_monitoring_task(OLD_API_URL, report)

        # Get data from NEW API
        new_data = create_monitoring_task(NEW_API_URL, report)

        if old_data and new_data:
            monitoring_task_queue.append({
                "task_name_old": old_data["task_name"],
                "task_uid_old": old_data["task_id"],
                "job_id_old": old_data["job_id"],
                "task_name_new": new_data["task_name"],
                "task_uid_new": new_data["task_id"],
                "job_id_new": new_data["job_id"]
            })

    with open("job_queue.json", "w") as f:
        json.dump(monitoring_task_queue, f, indent=4)

    print("\n✅ job_queue.json updated with your custom keys.")
