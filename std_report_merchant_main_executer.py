# main_executor.py
from std_report_merchant_api_handler import create_monitoring_task
import json

OLD_API_URL = 'https://sandbox.portal.juspay.in/api/monitoring/task'
NEW_API_URL = 'https://sandbox.portal.juspay.in/reporting/task'

REPORTS_TO_EXECUTE = [
    {
        "task_name": "ALT ID Provisioning Success Report",
        "task_description": "Provides consolidated summary of successful ALT_ID provisioning requests across sub-merchants, card networks.",
        "mail": ["samarth.rao@juspay.in", "rahul.jagdhane@juspay.in"],
        "standard_report_type": "ALTID_PROVISION_SR"
    },
    {
        "task_name": "Offer Benefit Report",
        "task_description": "This report provides details of every offer applied during a transaction attempt, with each offer detail listed in a separate row.",
        "mail": [
            "samarth.rao@juspay.in",
            "rahul.jagdhane@juspay.in"
        ],
        "standard_report_type": "OFFER_BENEFIT"
    },
    # {
    #     "task_name": "Mandate Retry and Retargeting Report OLD_API",
    #     "task_description": "Provides summarised report on Mandate Retry and Retargeting business metrics.",
    #     "mail": [
    #         "samarth.rao@juspay.in",
    #         "rahul.jagdhane@juspay.in"
    #     ],
    #     "standard_report_type": "MANDATE_RETRY"
    # },
    # {
    #     "task_name": "Failed and Manual Review Refund Report OLD_API",
    #     "task_description": "This report contains refunds which Failed or moved to Manual Review on the previous day.",
    #     "mail": [
    #         "samarth.rao@juspay.in",
    #         "rahul.jagdhane@juspay.in"

    #     ],
    #     "standard_report_type": "FAILED_MANUAL_REFUND"
    # }, {
    #     "task_name": "ALT ID Provisioning Report",
    #     "task_description": "Provides day wise summary of ALT_ID provisioning requests across sub-merchants, card networks, issuers.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "ALTID_PROVISION"
    # },
    # {
    #     "task_name": "Card Bin Token Bin Mapping Report",
    #     "task_description": "Mapping between the Token bin and the corresponding Card bin.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "CARD_BIN_TOKEN_BIN_MAPPING"
    # },
    # {
    #     "task_name": "Payout Validation Report",
    #     "task_description": "This report provides a summary about the details of the validations performed on beneficiary information—such as bank account numbers, IFSC codes, UPI_IDs — prior to processing payouts.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "PAYOUT_VALIDATION_REPORT"
    # },
    # {
    #     "task_name": "Gateway Health Based Routing",
    #     "task_description": "This report provides the detailed breakdown of transactions saved via Gateway Health Based Routing.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "HEALTH_ROUTING"
    # },
    # {
    #     "task_name": "Silent Retry Report",
    #     "task_description": "This report provides the detailed breakdown of transactions saved via Silent Retry.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "SILENT_RETRY"
    # },
    # {
    #     "task_name": "Payout Reversed Transactions Report",
    #     "task_description": "This report is a document or summary that provides information about various Reversed financial transactions or payments made by an organization to individuals, vendors, employees, or other entities.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "PAYOUT_REVERSAL"
    # },
    # {
    #     "task_name": "Van Transactions Report",
    #     "task_description": "This report provides details of all orders where payment was done via VAN.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "PAYOUT_VAN_TXN"
    # },
    # {
    #     "task_name": "Payout Fulfillment Txn Report",
    #     "task_description": "A payout fulfillment report is a document or summary that provides information about various financial transactions or payments made by an organization to individuals, vendors, employees, or other entities.",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "PAYOUT_FULFILLMENT"
    # },
    # {
    #     "task_name": "New Orders Report",
    #     "task_description": "This report provides details of orders with status as NEW. This is the status if order is created but transaction is not attempted on it",
    #     "mail": [
    #         "samarth.rao@juspay.in"
    #     ],
    #     "standard_report_type": "NEW_ORDERS"
    # }

]

monitoring_task_queue = []

if __name__ == "__main__":
    for report in REPORTS_TO_EXECUTE:
        # Trigger OLD API (Will automatically have 'OLD' in name)
        res_old, job_old = create_monitoring_task(OLD_API_URL, report)

        # Trigger NEW API (Will automatically have 'NEW' in name)
        res_new, job_new = create_monitoring_task(NEW_API_URL, report)

        if job_old and job_new:
            monitoring_task_queue.append({
                "task_name": report["task_name"],
                "old_job_id": job_old,
                "new_job_id": job_new
            })

    with open("job_queue.json", "w") as f:
        json.dump(monitoring_task_queue, f, indent=4)
    print("\n✅ Queue updated with suffixes and saved to job_queue.json")
