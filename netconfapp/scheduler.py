from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .backup import perform_backup
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def schedule_backup(backup_schedule, user):
    job_id = f"backup_{backup_schedule.id}"
    run_date = datetime.combine(backup_schedule.schedule_date, backup_schedule.schedule_time)
    
    # Remove any existing job with the same ID
    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
    
    # Schedule the job with a reference to the function and arguments
    scheduler.add_job(
        perform_backup,  # Pass the function reference
        'date',
        run_date=run_date,
        id=job_id,
        args=[backup_schedule.device.id, user.id],  # Pass arguments to the function
        replace_existing=True
    )

def start_scheduler():
    scheduler.start()
