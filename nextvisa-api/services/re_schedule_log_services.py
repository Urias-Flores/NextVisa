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
        
        # Truncate content if too long to prevent Cloudflare errors
        MAX_CONTENT_LENGTH = 5000
        content = re_schedule_log.content
        if len(content) > MAX_CONTENT_LENGTH:
            logger.warning(f"Log content truncated from {len(content)} to {MAX_CONTENT_LENGTH} characters")
            content = content[:MAX_CONTENT_LENGTH] + "... [truncated]"
            re_schedule_log.content = content
        
        data = re_schedule_log.model_dump(mode='json')
        logger.debug(f"Creating re-schedule log for re_schedule={data.get('re_schedule')}, state={data.get('state')}, content_length={len(content)}")
        
        response = db.from_("re_schedule_log").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return ReScheduleLogResponse(**response.data[0])
        raise Exception("Failed to create re-schedule log - no data returned")
    except Exception as e:
        logger.error(f"Unable to create re-schedule log for re_schedule={re_schedule_log.re_schedule}: {e}")
        # Don't re-raise - log creation should not break the main process
        return None