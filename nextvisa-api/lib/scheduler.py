import logging
import requests
import threading
from datetime import datetime, timezone
from typing import Dict, Optional
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from services import re_schedule_services, applicant_services, configuration_services, applicant_web_services, re_schedule_log_services
from models.re_schedule import ScheduleStatus, ReScheduleUpdate
from models.re_schedule_log import ReScheduleLogCreate, LogState
from models.applicant import ApplicantUpdate
from lib.security import decrypt_password

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[int, str] = {}
        self.lock = Lock()

        if not self.scheduler.running:
            self.scheduler.start()
    
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

        # Check for re-schedule that are in SCHEDULED status
        re_schedules = re_schedule_services.get_re_schedules_by_status(ScheduleStatus.SCHEDULED.value)

        # Schedule each re-schedule
        for schedule in re_schedules:
            if schedule.get("id") in self.jobs:
                continue

            start_datetime = datetime.strptime(
                schedule.get("start_datetime").replace("T", " "), 
                "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
            
            if start_datetime < datetime.now(timezone.utc):
                logger.info(f"Re-schedule {schedule.get('id')} is overdue, skipping")

                re_schedule_services.update_re_schedule(
                    schedule.get("id"),
                    ReScheduleUpdate(
                        status=ScheduleStatus.FAILED,
                        error="Re-schedule process could not be completed and now is overdue"
                    )
                )
                continue

            self.schedule_re_schedule(schedule.get("id"))

    def stop(self):
        self.scheduler.shutdown()

    def schedule_re_schedule(self, schedule_id: int):
        threading.Thread(
            target=self._run_scheduling, 
            args=(schedule_id,), 
            daemon=True
        ).start()

    def _run_scheduling(self, schedule_id: int):
        schedule = re_schedule_services.get_re_schedule_by_id(schedule_id)
        if not schedule:
            logger.warning(f"Re-schedule {schedule_id} not found")
            return
        
        run_at = schedule.get("start_datetime")
        if not run_at:
            logger.warning(f"Re-schedule {schedule_id} has no start datetime")
            return

        # Verify that the applicant login first
        applicant = applicant_services.get_applicant_with_password(schedule.get("applicant"))
        if not applicant:
            logger.warning(f"Applicant {schedule.get('applicant')} not found")
            return
        decrypted_password = decrypt_password(applicant.get("password"))
        re_schedule_log_services.create_re_schedule_log(
            ReScheduleLogCreate(
                re_schedule=schedule_id,
                state=LogState.WARNING,
                content="Applicant login attempt"
            )
        )
        result = applicant_web_services.test_credentials(applicant.get("email"), decrypted_password)

        if not result or not result.get("success"):
            logger.warning(f"Applicant {schedule.get('applicant')} login failed")

            re_schedule_log_services.create_re_schedule_log(
                ReScheduleLogCreate(
                    re_schedule=schedule_id,
                    state=LogState.ERROR,
                    content="Attempt to login failed"
                )
            )

            re_schedule_services.update_re_schedule(
                schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.FAILED, error="Failed to login with current credentials")
            )

            applicant_services.update_applicant_re_schedule_status(
                schedule.get("applicant"), 
                "LOGIN_PENDING"
            )
            return

        re_schedule_log_services.create_re_schedule_log(
            ReScheduleLogCreate(
                re_schedule=schedule_id,
                state=LogState.SUCCESS,
                content="Applicant login successful. Scheduling re-schedule"
            )
        )

        with self.lock:
            job = self.scheduler.add_job(
                applicant_web_services.process_re_schedule, 
                'date', 
                run_date=run_at,
                args=[schedule_id],
                id=f"rs_{schedule_id}"
            )
            
            self.jobs[schedule_id] = job
            logger.info(f"Scheduled one-time job for re-schedule {schedule_id} at {run_at}")
            re_schedule_services.update_re_schedule(
                schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.SCHEDULED)
            )
            logger.info(f"Updated re-schedule {schedule_id} status to SCHEDULED")

            re_schedule_log_services.create_re_schedule_log(
                ReScheduleLogCreate(
                    re_schedule=schedule_id,
                    state=LogState.INFO,
                    content="Re-schedule process scheduled successfully"
                )
            )

# Singleton instance
scheduler = Scheduler()