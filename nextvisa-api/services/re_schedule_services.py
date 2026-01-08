from lib.database import SupabaseConnection
from lib.scheduler import scheduler
from models.re_schedule import ReScheduleCreate, ReScheduleUpdate
from lib.exceptions import DatabaseException
import logging
from typing import List, Optional
from lib.scheduler import scheduler

logger = logging.getLogger(__name__)

TABLE_NAME = "re_schedule"


class ReScheduleNotFoundException(Exception):
    """Exception raised when a re-schedule record is not found"""
    def __init__(self, re_schedule_id: int):
        self.re_schedule_id = re_schedule_id
        self.message = f"Re-schedule with ID {re_schedule_id} not found"
        super().__init__(self.message)


def _get_db():
    """Helper function to get database client"""
    return SupabaseConnection.get_client()


def get_all_re_schedules(limit: Optional[int] = None, offset: Optional[int] = None) -> List[dict]:
    """
    Fetch all re-schedule records from the database
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of re-schedule dictionaries
        
    Raises:
        DatabaseException: If database operation fails
    """
    try:
        db = _get_db()
        query = db.table(TABLE_NAME).select("*").order("created_at", desc=True)
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        response = query.execute()
        logger.info(f"Successfully fetched {len(response.data)} re-schedule records")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch re-schedules: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_all_re_schedules", str(e))


def get_re_schedule_by_id(re_schedule_id: int) -> dict:
    """
    Fetch a single re-schedule record by ID
    
    Args:
        re_schedule_id: The ID of the re-schedule to fetch
        
    Returns:
        Re-schedule dictionary
        
    Raises:
        ReScheduleNotFoundException: If re-schedule doesn't exist
        DatabaseException: If database operation fails
    """
    if not re_schedule_id:
        raise ValueError("Re-schedule ID is required")
        
    try:
        db = _get_db()
        response = db.table(TABLE_NAME).select("*").eq("id", re_schedule_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"Re-schedule with ID {re_schedule_id} not found")
            raise ReScheduleNotFoundException(re_schedule_id)
            
        logger.info(f"Successfully fetched re-schedule with ID {re_schedule_id}")
        return response.data[0]
    except ReScheduleNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_re_schedule_by_id", str(e))


def get_re_schedules_by_applicant(applicant_id: int, limit: Optional[int] = None) -> List[dict]:
    """
    Fetch all re-schedule records for a specific applicant
    
    Args:
        applicant_id: The ID of the applicant
        limit: Maximum number of records to return
        
    Returns:
        List of re-schedule dictionaries
        
    Raises:
        DatabaseException: If database operation fails
    """
    if not applicant_id:
        raise ValueError("Applicant ID is required")
        
    try:
        db = _get_db()
        query = db.table(TABLE_NAME).select("*").eq("applicant", applicant_id).order("created_at", desc=True)
        
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        logger.info(f"Successfully fetched {len(response.data)} re-schedule records for applicant {applicant_id}")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch re-schedules for applicant {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_re_schedules_by_applicant", str(e))


def get_re_schedules_by_status(status: str, limit: Optional[int] = None) -> List[dict]:
    """
    Fetch re-schedule records by status
    
    Args:
        status: Status value to filter by
        limit: Maximum number of records to return
        
    Returns:
        List of re-schedule dictionaries
        
    Raises:
        DatabaseException: If database operation fails
    """
    if not status:
        raise ValueError("Status is required")
        
    try:
        db = _get_db()
        query = db.table(TABLE_NAME).select("*").eq("status", status).order("created_at", desc=True)
        
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        logger.info(f"Successfully fetched {len(response.data)} re-schedule records with status {status}")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch re-schedules by status {status}: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_re_schedules_by_status", str(e))

def create_re_schedule(re_schedule_data: ReScheduleCreate) -> dict:
    """
    Create a new re-schedule record
    
    Args:
        re_schedule_data: ReScheduleCreate schema with re-schedule details
        
    Returns:
        Created re-schedule dictionary
        
    Raises:
        DatabaseException: If database operation fails
    """
    try:
        db = _get_db()
        # Convert Pydantic model to dict
        re_schedule_dict = re_schedule_data.model_dump()
        
        # Convert datetime objects to ISO format strings if present
        if re_schedule_dict.get('start_datetime'):
            re_schedule_dict['start_datetime'] = re_schedule_dict['start_datetime'].isoformat()
        if re_schedule_dict.get('end_datetime'):
            re_schedule_dict['end_datetime'] = re_schedule_dict['end_datetime'].isoformat()
        
        # Insert into database
        response = db.table(TABLE_NAME).insert(re_schedule_dict).execute()
        
        if not response.data or len(response.data) == 0:
            raise DatabaseException("create_re_schedule", "No data returned after insert")
            
        created_re_schedule = response.data[0]
        logger.info(f"Successfully created re-schedule with ID {created_re_schedule.get('id')}")

        scheduler.schedule_re_schedule(created_re_schedule.get('id'))
        logger.info(f"Scheduled re-schedule {created_re_schedule.get('id')} ready for execution")
        return created_re_schedule
    except Exception as e:
        logger.error(f"Failed to create re-schedule: {str(e)}", exc_info=True)
        raise DatabaseException("create_re_schedule", str(e))


def update_re_schedule(re_schedule_id: int, re_schedule_data: ReScheduleUpdate) -> dict:
    """
    Update an existing re-schedule record
    
    Args:
        re_schedule_id: The ID of the re-schedule to update
        re_schedule_data: ReScheduleUpdate schema with fields to update
        
    Returns:
        Updated re-schedule dictionary
        
    Raises:
        ReScheduleNotFoundException: If re-schedule doesn't exist
        DatabaseException: If database operation fails
    """
    if not re_schedule_id:
        raise ValueError("Re-schedule ID is required")
        
    # First check if re-schedule exists
    get_re_schedule_by_id(re_schedule_id)
    
    try:
        db = _get_db()
        # Only include fields that were actually provided
        update_dict = re_schedule_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            logger.warning(f"No fields to update for re-schedule {re_schedule_id}")
            return get_re_schedule_by_id(re_schedule_id)
        
        # Convert datetime objects to ISO format strings if present
        if 'start_datetime' in update_dict and update_dict['start_datetime']:
            update_dict['start_datetime'] = update_dict['start_datetime'].isoformat()
        if 'end_datetime' in update_dict and update_dict['end_datetime']:
            update_dict['end_datetime'] = update_dict['end_datetime'].isoformat()
            
        response = db.table(TABLE_NAME).update(update_dict).eq("id", re_schedule_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise DatabaseException("update_re_schedule", "No data returned after update")
        
        updated_re_schedule = response.data[0]
        logger.info(f"Successfully updated re-schedule with ID {re_schedule_id}")
        return updated_re_schedule
    except ReScheduleNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to update re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise DatabaseException("update_re_schedule", str(e))


def delete_re_schedule(re_schedule_id: int) -> bool:
    """
    Delete a re-schedule record
    
    Args:
        re_schedule_id: The ID of the re-schedule to delete
        
    Returns:
        True if deletion was successful
        
    Raises:
        ReScheduleNotFoundException: If re-schedule doesn't exist
        DatabaseException: If database operation fails
    """
    if not re_schedule_id:
        raise ValueError("Re-schedule ID is required")
        
    # First check if re-schedule exists
    re_schedule = get_re_schedule_by_id(re_schedule_id)
    
    # Remove job from scheduler if it's scheduled or processing
    if re_schedule.get("status") in ["SCHEDULED", "PROCESSING"]:
        try:
            scheduler.remove_job(re_schedule_id)
            logger.info(f"Removed job for re-schedule {re_schedule_id} from scheduler")
        except Exception as e:
            logger.warning(f"Could not remove job from scheduler for re-schedule {re_schedule_id}: {e}")

    try:
        db = _get_db()
        response = db.table(TABLE_NAME).delete().eq("id", re_schedule_id).execute()
        logger.info(f"Successfully deleted re-schedule with ID {re_schedule_id}")
        return True
    except ReScheduleNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise DatabaseException("delete_re_schedule", str(e))
