# main_executor.py
from admin_report_merchant_api_handler import create_monitoring_task
import json

# Updated Staging Endpoints
OLD_API_URL = 'https://euler-x.internal.staging.mum.juspay.net/api/monitoring/task'
NEW_API_URL = 'https://euler-x.internal.staging.mum.juspay.net/reporting/task'

REPORTS_TO_EXECUTE = [
    {
        "task_name": "Transaction Refund Report",
        "task_description": "Comprehensive report representing previous day transactions and refunds data.",
        "mail": ["samarth.rao@juspay.in",
                 "rahul.jagdhane@juspay.in"],
        "standard_report_type": "TXN_REFUND"
    },
    {
        "task_name": "ALT ID Provisioning Success Report",
        "task_description": "Provides consolidated summary of successful ALT_ID provisioning requests across sub-merchants, card networks.",
        "mail": ["samarth.rao@juspay.in", "rahul.jagdhane@juspay.in"],
        "standard_report_type": "ALTID_PROVISION_SR"
    }
]

monitoring_task_queue = []

if __name__ == "__main__":
    print("--- Starting Internal Staging Execution ---")
    for report in REPORTS_TO_EXECUTE:
        # Trigger OLD API
        res_old, job_old = create_monitoring_task(OLD_API_URL, report)

        # Trigger NEW API
        res_new, job_new = create_monitoring_task(NEW_API_URL, report)

        if job_old and job_new:
            monitoring_task_queue.append({
                "task_name": report["task_name"],
                "old_job_id": job_old,
                "new_job_id": job_new
            })

    with open("job_queue.json", "w") as f:
        json.dump(monitoring_task_queue, f, indent=4)
    print("\n✅ Staging Queue saved to job_queue.json")
