import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Optional
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from services import re_schedule_services, applicant_services, configuration_services, applicant_web_services
from models.re_schedule import ScheduleStatus, ReScheduleUpdate

logger = logging.getLogger(__name__)


class StateMachine:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[int, str] = {}
        self.applicant_jobs: Dict[int, str] = {}
        self.lock = Lock()
        self.config: Optional[Dict] = None
        self.scan_interval = 60

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
        self.config = configuration_services.get_configuration()
        if not self.config:
            logger.warning("No configuration found. State machine will not start scanning.")
            return

        logger.info(f"Starting ReScheduleStateMachine with scan interval {self.scan_interval}s")
        self.scheduler.add_job(self.scan_and_schedule_reschedules, 'interval', seconds=self.scan_interval, id='scan_pending_rs')

    def stop(self):
        try:
            self.scheduler.shutdown(wait=False)
        except Exception as ex:
            logger.error("Error shutting down scheduler", ex, exc_info=True)
            pass

    def scan_and_schedule_reschedules(self):
        try:
            logger.info("Scanning for pending re-schedules")
            schedules = re_schedule_services.get_re_schedules_by_status(ScheduleStatus.PENDING.value, limit=100)
            schedules_to_run = []
            for schedule in schedules:
                dt_str = schedule.get("start_datetime")
                if not dt_str:
                    continue
                dt_str = dt_str.replace("T", " ")
                start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                
                if start_dt <= datetime.now(timezone.utc):
                    schedules_to_run.append(schedule)

            if not schedules_to_run:
                logger.info("No pending re-schedules found")
                return

            for schedule in schedules_to_run:
                schedule_id = schedule.get('id')
                run_at = schedule.get("start_datetime")

                if schedule_id is None or run_at is None:
                    return

                with self.lock:
                    job = self.scheduler.add_job(
                        applicant_web_services.process_re_schedule, 
                        'date', 
                        run_date=run_at,
                        args=[schedule_id],
                        id=f"rs_{schedule_id}"
                    )
                    
                    logger.info(f"Scheduled one-time job for re-schedule {schedule_id} at {run_at}")
                    re_schedule_services.update_re_schedule(
                        schedule_id,
                        ReScheduleUpdate(status=ScheduleStatus.SCHEDULED)
                    )
                    logger.info(f"Updated re-schedule {schedule_id} status to SCHEDULED")

        except Exception as e:
            logger.error(f"Error scanning pending re-schedules: {e}", exc_info=True)

    def _remove_job(self, re_schedule_id: int):
        with self.lock:
            job_id = self.jobs.pop(re_schedule_id, None)
            if job_id:
                try:
                    self.scheduler.remove_job(job_id)
                except Exception:
                    pass
        with self.lock:
            job_id = self.applicant_jobs.pop(re_schedule_id, None)
            if job_id:
                try:
                    self.scheduler.remove_job(job_id)
                except Exception:
                    pass

# Singleton instance
state_machine = StateMachine()
