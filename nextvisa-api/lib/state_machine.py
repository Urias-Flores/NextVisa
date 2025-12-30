import logging
import requests
from typing import Dict, Optional
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from services import re_schedule_services, applicant_services, configuration_services, applicant_web_services
from models.re_schedule import ScheduleStatus

logger = logging.getLogger(__name__)


class StateMachine:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[int, str] = {}
        self.applicant_jobs: Dict[int, str] = {}
        self.lock = Lock()
        self.config: Optional[Dict] = None

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
        # Load configuration
        self.config = configuration_services.get_configuration()
        if not self.config:
            logger.warning("No configuration found. State machine will not start scanning.")
            return
        scan_interval = max(60, int(self.config.sleep_time))
        logger.info(f"Starting ReScheduleStateMachine with scan interval {scan_interval}s")
        # Periodically scan for pending jobs
        self.scheduler.add_job(self.scan_and_schedule_reschedules, 'interval', seconds=scan_interval, id='scan_pending_rs')
        # self.scheduler.add_job(self.scan_and_schedule_applicants, 'interval', seconds=scan_interval, id='scan_pending_app')

    def stop(self):
        try:
            self.scheduler.shutdown(wait=False)
        except Exception as ex:
            logger.error("Error shutting down scheduler", ex, exc_info=True)
            pass

    def scan_and_schedule_reschedules(self):
        try:
            pending = re_schedule_services.get_re_schedules_by_status(ScheduleStatus.PENDING.value, limit=50)
            candidates = pending
            logger.info(f"Found {len(candidates)} re-schedule candidates (PENDING)")

            for rs in candidates:
                rs_id = rs.get('id')
                if rs_id is None:
                    continue
                with self.lock:
                    if rs_id in self.jobs:
                        continue
                    interval = max(5, int(self.config.get("sleep_time")))
                    job = self.scheduler.add_job(applicant_web_services.process_re_schedule, 'interval', seconds=interval, args=[rs_id], id=f"rs_{rs_id}")
                    self.jobs[rs_id] = job.id
                    logger.info(f"Scheduled processing job for re-schedule {rs_id}")
        except Exception as e:
            logger.error(f"Error scanning pending re-schedules: {e}", exc_info=True)

    def scan_and_schedule_applicants(self):
        try:
            login_pending = applicant_services.get_applicants_by_re_schedule_status("LOGIN_PENDING", limit=50)
            logger.info(f"Found {len(login_pending)} applicants with LOGIN_PENDING")
            for ap in login_pending:
                ap_id = ap.get('id')
                if ap_id is None:
                    continue
                with self.lock:
                    if ap_id in self.applicant_jobs:
                        continue
                    interval = max(10, int(self.config.sleep_time))
                    job = self.scheduler.add_job(self._process_applicant_login, 'interval', seconds=interval, args=[ap_id], id=f"app_{ap_id}")
                    self.applicant_jobs[ap_id] = job.id
                    logger.info(f"Scheduled login-check job for applicant {ap_id}")
        except Exception as e:
            logger.error(f"Error scanning applicants LOGIN_PENDING: {e}", exc_info=True)

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

    def _copy_cookies(self, driver, session: requests.Session):
        for c in driver.get_cookies():
            session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

    def _get_dates_via_requests(self, driver, days_url: str, referer_url: str):
        session = requests.Session()
        self._copy_cookies(driver, session)
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": referer_url,
            "User-Agent": driver.execute_script("return navigator.userAgent;")
        }
        r = session.get(days_url, headers=headers, allow_redirects=True, timeout=15)
        try:
            return r.json()
        except ValueError:
            return []

    def _process_applicant_login(self, applicant_id: int):
        try:
            applicant = applicant_services.get_applicant_with_password(applicant_id)
            email = applicant.get('email')
            password = applicant.get('password')
            if not email or not password:
                logger.warning(f"Applicant {applicant_id} missing email or password")
                return
            result = applicant_web_services.test_credentials(email, password)
            if result.get("success") and result.get("schedule"):
                schedule_number = result["schedule"]
                applicant_services.update_applicant_schedule(applicant_id, schedule_number)
                applicant_services.update_applicant_re_schedule_status(applicant_id, "PENDING")
                logger.info(f"Applicant {applicant_id} credentials verified; schedule set {schedule_number}; status -> PENDING")
                self._remove_job(applicant_id)
            elif not result.get("success"):
                logger.warning(f"Applicant {applicant_id} login failed: {result.get('error')}")
            else:
                logger.info(f"Applicant {applicant_id} login ok but schedule not found")
        except Exception as e:
            logger.error(f"Error processing applicant login {applicant_id}: {e}", exc_info=True)


# Singleton instance
state_machine = StateMachine()
