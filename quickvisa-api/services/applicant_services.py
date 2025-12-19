from lib.database import SupabaseConnection
from models.applicant import ApplicantCreate, ApplicantUpdate, ApplicantResponse
from lib.exceptions import ApplicantNotFoundException, DatabaseException
from lib.security import encrypt_password
from models.applicant import ApplicantStatus
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

TABLE_NAME = "applicant"


def _get_db():
    """Helper function to get database client"""
    return SupabaseConnection.get_client()


def _prepare_applicant_data(applicant_dict: dict) -> dict:
    """
    Prepare applicant data for storage, including password hashing
    
    Args:
        applicant_dict: Dictionary with applicant data
        
    Returns:
        Dictionary with hashed password if present
    """
    if 'password' in applicant_dict and applicant_dict['password']:
        applicant_dict['password'] = encrypt_password(applicant_dict['password'])
    return applicant_dict


def get_all_applicants(limit: Optional[int] = None, offset: Optional[int] = None) -> List[dict]:
    """
    Fetch all applicants from the database
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of applicant dictionaries
        
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
        logger.info(f"Successfully fetched {len(response.data)} applicants")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch applicants: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_all_applicants", str(e))


def get_applicant_by_id(applicant_id: int) -> dict:
    """
    Fetch a single applicant by ID
    
    Args:
        applicant_id: The ID of the applicant to fetch
        
    Returns:
        Applicant dictionary
        
    Raises:
        ApplicantNotFoundException: If applicant doesn't exist
        DatabaseException: If database operation fails
    """
    if not applicant_id:
        raise ValueError("Applicant ID is required")
        
    try:
        db = _get_db()
        response = db.table(TABLE_NAME).select("*").eq("id", applicant_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"Applicant with ID {applicant_id} not found")
            raise ApplicantNotFoundException(applicant_id)
            
        logger.info(f"Successfully fetched applicant with ID {applicant_id}")
        return response.data[0]
    except ApplicantNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch applicant {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_applicant_by_id", str(e))


def create_applicant(applicant_data: ApplicantCreate) -> dict:
    """
    Create a new applicant with hashed password
    
    Args:
        applicant_data: ApplicantCreate schema with applicant details
        
    Returns:
        Created applicant dictionary (without password)
        
    Raises:
        DatabaseException: If database operation fails
    """
    try:
        db = _get_db()
        # Convert Pydantic model to dict
        applicant_dict = applicant_data.model_dump()
        
        # Hash password before storing
        applicant_dict = _prepare_applicant_data(applicant_dict)
        
        # Insert into database
        response = db.table(TABLE_NAME).insert(applicant_dict).execute()
        
        if not response.data or len(response.data) == 0:
            raise DatabaseException("create_applicant", "No data returned after insert")
            
        created_applicant = response.data[0]
        
        # Remove password from response for security
        if 'password' in created_applicant:
            del created_applicant['password']
            
        logger.info(f"Successfully created applicant with ID {created_applicant.get('id')}")
        return created_applicant
    except Exception as e:
        logger.error(f"Failed to create applicant: {str(e)}", exc_info=True)
        raise DatabaseException("create_applicant", str(e))


def update_applicant(applicant_id: int, applicant_data: ApplicantUpdate) -> dict:
    """
    Update an existing applicant (hashes password if provided)
    
    Args:
        applicant_id: The ID of the applicant to update
        applicant_data: ApplicantUpdate schema with fields to update
        
    Returns:
        Updated applicant dictionary (without password)
        
    Raises:
        ApplicantNotFoundException: If applicant doesn't exist
        DatabaseException: If database operation fails
    """
    if not applicant_id:
        raise ValueError("Applicant ID is required")
        
    # First check if applicant exists
    get_applicant_by_id(applicant_id)
    
    try:
        db = _get_db()
        # Only include fields that were actually provided
        update_dict = applicant_data.model_dump(exclude_unset=True)
        
        if not update_dict:
            logger.warning(f"No fields to update for applicant {applicant_id}")
            return get_applicant_by_id(applicant_id)
        
        # Hash password if it's being updated
        if 'password' in update_dict:
            update_dict = _prepare_applicant_data(update_dict)
            
        response = db.table(TABLE_NAME).update(update_dict).eq("id", applicant_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise DatabaseException("update_applicant", "No data returned after update")
        
        updated_applicant = response.data[0]
        
        # Remove password from response for security
        if 'password' in updated_applicant:
            del updated_applicant['password']
            
        logger.info(f"Successfully updated applicant with ID {applicant_id}")
        return updated_applicant
    except ApplicantNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to update applicant {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException("update_applicant", str(e))


def delete_applicant(applicant_id: int) -> bool:
    """
    Delete an applicant
    
    Args:
        applicant_id: The ID of the applicant to delete
        
    Returns:
        True if deletion was successful
        
    Raises:
        ApplicantNotFoundException: If applicant doesn't exist
        DatabaseException: If database operation fails
    """
    if not applicant_id:
        raise ValueError("Applicant ID is required")
        
    # First check if applicant exists
    get_applicant_by_id(applicant_id)
    



def get_applicant_with_password(applicant_id: int) -> dict:
    """
    Get applicant data including the password field (for credential testing)
    
    Args:
        applicant_id: ID of the applicant
        
    Returns:
        Applicant dictionary including password
        
    Raises:
        ApplicantNotFoundException: If applicant not found
        DatabaseException: If database operation fails
    """
    try:
        db = _get_db()
        response = db.table(TABLE_NAME).select("*").eq("id", applicant_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise ApplicantNotFoundException(f"Applicant with ID {applicant_id} not found")
        
        return response.data[0]
    except ApplicantNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error fetching applicant with password {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to fetch applicant: {str(e)}")


def update_applicant_schedule(applicant_id: int, schedule_number: str) -> dict:
    """
    Update applicant's schedule number
    
    Args:
        applicant_id: ID of the applicant
        schedule_number: Schedule number to set
        
    Returns:
        Updated applicant dictionary
        
    Raises:
        ApplicantNotFoundException: If applicant not found
        DatabaseException: If database operation fails
    """
    try:
        db = _get_db()
        
        # Check if applicant exists
        existing = db.table(TABLE_NAME).select("id").eq("id", applicant_id).execute()
        if not existing.data or len(existing.data) == 0:
            raise ApplicantNotFoundException(f"Applicant with ID {applicant_id} not found")
        
        # Update schedule
        update_data = {
            "schedule": schedule_number,
            "re_schedule_status": ApplicantStatus.PENDING.value
        }
        response = db.table(TABLE_NAME).update(update_data).eq("id", applicant_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise DatabaseException("Update operation returned no data")
        
        logger.info(f"Successfully updated schedule for applicant {applicant_id}")
        return response.data[0]
        
    except ApplicantNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Error updating applicant schedule {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update applicant schedule: {str(e)}")


def get_applicants_by_re_schedule_status(status: str, limit: Optional[int] = None) -> List[dict]:
    """
    Fetch applicants filtered by re_schedule_status
    
    Args:
        status: Status to filter by (e.g., 'LOGIN_PENDING', 'PENDING')
        limit: Maximum number of records to return
        
    Returns:
        List of applicant dictionaries
    """
    try:
        db = _get_db()
        query = db.table(TABLE_NAME).select("*").eq("re_schedule_status", status).order("created_at", desc=True)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        logger.info(f"Successfully fetched {len(response.data)} applicants with status {status}")
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch applicants by re_schedule_status {status}: {str(e)}", exc_info=True)
        raise DatabaseException("fetch_applicants_by_re_schedule_status", str(e))


def update_applicant_re_schedule_status(applicant_id: int, status: str) -> dict:
    """
    Update an applicant's re_schedule_status
    
    Args:
        applicant_id: ID of the applicant
        status: New status string
        
    Returns:
        Updated applicant dictionary
    """
    try:
        db = _get_db()
        # Ensure applicant exists
        existing = db.table(TABLE_NAME).select("id").eq("id", applicant_id).execute()
        if not existing.data or len(existing.data) == 0:
            raise ApplicantNotFoundException(f"Applicant with ID {applicant_id} not found")
        update_data = {"re_schedule_status": status}
        response = db.table(TABLE_NAME).update(update_data).eq("id", applicant_id).execute()
        if not response.data or len(response.data) == 0:
            raise DatabaseException("Update operation returned no data")
        logger.info(f"Successfully updated re_schedule_status for applicant {applicant_id} -> {status}")
        return response.data[0]
    except ApplicantNotFoundException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error(f"Error updating applicant re_schedule_status {applicant_id}: {str(e)}", exc_info=True)
        raise DatabaseException(f"Failed to update applicant re_schedule_status: {str(e)}")
