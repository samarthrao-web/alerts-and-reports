# main_executor.py

from merchant_api_handler import create_monitoring_task
from Transaction_dimension import ALL_DIMENSION_SETS # Import the consolidated list

# Define the two distinct API endpoints
OLD_API_URL = 'https://sandbox.portal.juspay.in/api/monitoring/task'
NEW_API_URL = 'https://sandbox.portal.juspay.in/reporting/task'

# This list stores dictionaries, acting as the queue (FIFO logic)
monitoring_task_queue = [] 

if __name__ == "__main__":
    
    print(f"\n{'='*70}")
    print("STARTING DUAL API EXECUTION AND JOB QUEUEING")
    print(f"{'='*70}")

    for dim_list, dim_name in ALL_DIMENSION_SETS:
        
        print(f"\n\n>>>>>>>>>>> PROCESSING DIMENSION SET: {dim_name} <<<<<<<<<<<<")
        print(f"Dimensions: {dim_list}")

        # --- 1. Execute OLD API Call ---
        response_id_old, job_id_old = create_monitoring_task(
            url=OLD_API_URL,
            dimensions_list=dim_list,
            dim_name=dim_name + " (OLD API)",
            task_name=f"testing old api - {dim_name}"
        )
        
        # --- 2. Execute NEW API Call ---
        response_id_new, job_id_new = create_monitoring_task(
            url=NEW_API_URL,
            dimensions_list=dim_list,
            dim_name=dim_name + " (NEW API)",
            task_name=f"testing new api - {dim_name}"
        )
        
        # --- 3. Queue the Results ---
        
        if job_id_old and job_id_new:
            queue_entry = {
                "dimensions_name": dim_name,
                "dimensions": dim_list,
                "old_api_job_id": job_id_old,
                "new_api_job_id": job_id_new,
                "old_api_response_id": response_id_old,
                "new_api_response_id": response_id_new,
            }
            monitoring_task_queue.append(queue_entry)
            print(f"\n✅ SUCCESSFULLY QUEUED job IDs for {dim_name}.")
        else:
            print(f"\n❌ SKIPPING QUEUE for {dim_name}: One or both API calls failed to return a Job/Task ID.")
            
    
    # --- FINAL QUEUE INSPECTION ---
    
    print("\n" + "="*70)
    print("📋 FINAL MONITORING JOB QUEUE")
    print("="*70)
    
    if monitoring_task_queue:
        for i, item in enumerate(monitoring_task_queue):
            print(f"--- Q Item {i+1}: {item['dimensions_name']} ---")
            print(f"  Dimensions: {item['dimensions']}")
            print(f"  OLD API Job ID: {item['old_api_job_id']}")
            print(f"  NEW API Job ID: {item['new_api_job_id']}")
            print("-" * 30)
    else:
        print("The queue is empty. Check the console output above for API failures.")
    
    print(f"\n{'='*70}")
    print("✅ All processing complete!")
    print(f"{'='*70}")