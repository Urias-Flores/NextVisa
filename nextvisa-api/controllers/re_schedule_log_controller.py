from fastapi import APIRouter, HTTPException
from services import re_schedule_log_services
from typing import List
from models.re_schedule_log import ReScheduleLogResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/re-schedule-logs", tags=["re-schedule-logs"])

@router.get("/{re_schedule_id}", response_model=List[ReScheduleLogResponse])
async def get_logs_by_re_schedule(re_schedule_id: int):
    """Get all logs for a specific re-schedule process"""
    try:
        logs = re_schedule_log_services.get_re_schedule_log_by_re_schedule_id(re_schedule_id)
        return logs
    except Exception as e:
        logger.error(f"Error fetching re-schedule logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
