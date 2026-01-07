from lib.database import SupabaseConnection
from models.re_schedule_log import ReScheduleLogCreate, ReScheduleLogResponse
from lib.exceptions import DatabaseException
import logging

logger = logging.getLogger(__name__)

def get_re_schedule_log():
    try:
        db = SupabaseConnection.get_client()
        response = db.from_("re_schedule_log").select("*").execute()
        
        if response.data and len(response.data) > 0:
            return [ReScheduleLogResponse(**log) for log in response.data]
        return []
    except Exception as e:
        logger.error(f"Unable to get re-schedule logs: {e}")
        raise e

def get_re_schedule_log_by_re_schedule_id(re_schedule_id: int):
    try:
        db = SupabaseConnection.get_client()
        response = db.from_("re_schedule_log").select("*").eq("re_schedule", re_schedule_id).execute()
        
        if response.data and len(response.data) > 0:
            return [ReScheduleLogResponse(**log) for log in response.data]
        return []
    except Exception as e:
        logger.error(f"Unable to get re-schedule logs by re-schedule ID: {e}")
        raise e

def create_re_schedule_log(re_schedule_log: ReScheduleLogCreate):
    try:
        db = SupabaseConnection.get_client()
        data = re_schedule_log.model_dump(mode='json')
        response = db.from_("re_schedule_log").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return ReScheduleLogResponse(**response.data[0])
        raise Exception("Failed to create re-schedule log")
    except Exception as e:
        logger.error(f"Unable to create re-schedule log: {e}")
        raise e