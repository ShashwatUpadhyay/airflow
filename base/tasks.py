from background_task import background
from .models import Job
import time
from air.settings import BASE_DIR

# Use the @background decorator instead
# The 'schedule=1' tells it to run 1 second after being created.
@background(schedule=1)
def process_data_task(job_id):
    print(job_id)
    """
    This background job is now managed by django-background-tasks.
    The code inside the function remains exactly the same.
    """
    try:
        print(f"Job initiated {job_id}")
        
        job = Job.objects.get(job_id=job_id)
        job.status = "RUNNING"
        job.save()

        print(f"Processing job {job_id} with input: {job.input_data}")
        time.sleep(10) # Simulate long work
        output_location = f"{BASE_DIR}output_data/{job_id}.jpg"

        job.status = "SUCCEEDED"
        job.output_data = output_location
        job.save()
        
        print(f"Processing job {job_id} Done")
        
    except Exception as e:
        job = Job.objects.get(job_id=job_id)
        job.status = "FAILED"
        job.output_data = {"error": str(e)}
        job.save()
        print(f"job {job_id} Failed")
        
