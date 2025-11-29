from fastapi import APIRouter, HTTPException, status, Query
from models.re_schedule import ReScheduleCreate, ReScheduleUpdate, ReScheduleResponse
from services import re_schedule_services
from services.re_schedule_services import ReScheduleNotFoundException
from lib.exceptions import DatabaseException
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ReScheduleResponse])
def get_all_re_schedules(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of records to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of records to skip")
):
    """
    Get all re-schedule records with optional pagination
    
    - **limit**: Maximum number of records (1-100)
    - **offset**: Number of records to skip for pagination
    """
    try:
        re_schedules = re_schedule_services.get_all_re_schedules(limit=limit, offset=offset)
        return re_schedules
    except DatabaseException as e:
        logger.error(f"Database error while fetching re-schedules: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch re-schedules from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching re-schedules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/{re_schedule_id}", response_model=ReScheduleResponse)
def get_re_schedule(re_schedule_id: int):
    """
    Get a specific re-schedule record by ID
    
    - **re_schedule_id**: The ID of the re-schedule to retrieve
    """
    try:
        re_schedule = re_schedule_services.get_re_schedule_by_id(re_schedule_id)
        return re_schedule
    except ReScheduleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while fetching re-schedule {re_schedule_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch re-schedule from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/applicant/{applicant_id}", response_model=List[ReScheduleResponse])
def get_re_schedules_by_applicant(
    applicant_id: int,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get all re-schedule records for a specific applicant
    
    - **applicant_id**: The ID of the applicant
    - **limit**: Maximum number of records to return
    """
    try:
        re_schedules = re_schedule_services.get_re_schedules_by_applicant(applicant_id, limit=limit)
        return re_schedules
    except DatabaseException as e:
        logger.error(f"Database error while fetching re-schedules for applicant {applicant_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch re-schedules from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching re-schedules for applicant {applicant_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/", response_model=ReScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_re_schedule(re_schedule: ReScheduleCreate):
    """
    Create a new re-schedule record
    
    - **applicant**: ID of the applicant (required)
    - **start_datetime**: Start datetime (optional)
    - **end_datetime**: End datetime (optional)
    - **status**: Schedule status (default: PENDING)
    - **error**: Error message if any (optional)
    """
    try:
        created_re_schedule = re_schedule_services.create_re_schedule(re_schedule)
        return created_re_schedule
    except DatabaseException as e:
        logger.error(f"Database error while creating re-schedule: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create re-schedule in database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating re-schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/{re_schedule_id}", response_model=ReScheduleResponse)
def update_re_schedule(re_schedule_id: int, re_schedule: ReScheduleUpdate):
    """
    Update an existing re-schedule record
    
    - **re_schedule_id**: The ID of the re-schedule to update
    - All fields are optional - only provided fields will be updated
    """
    try:
        updated_re_schedule = re_schedule_services.update_re_schedule(re_schedule_id, re_schedule)
        return updated_re_schedule
    except ReScheduleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while updating re-schedule {re_schedule_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update re-schedule in database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while updating re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/{re_schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_re_schedule(re_schedule_id: int):
    """
    Delete a re-schedule record
    
    - **re_schedule_id**: The ID of the re-schedule to delete
    """
    try:
        re_schedule_services.delete_re_schedule(re_schedule_id)
        return None
    except ReScheduleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while deleting re-schedule {re_schedule_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete re-schedule from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while deleting re-schedule {re_schedule_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
