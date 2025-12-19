from fastapi import APIRouter, HTTPException, status, Query
from models.applicant import ApplicantCreate, ApplicantUpdate, ApplicantResponse
from services import applicant_services
from services import applicant_web_services
from lib.exceptions import ApplicantNotFoundException, DatabaseException
from typing import List, Optional
from lib.security import decrypt_password
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ApplicantResponse])
def get_all_applicants(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of records to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of records to skip")
):
    """
    Get all applicants with optional pagination
    
    - **limit**: Maximum number of records (1-100)
    - **offset**: Number of records to skip for pagination
    """
    try:
        applicants = applicant_services.get_all_applicants(limit=limit, offset=offset)
        return applicants
    except DatabaseException as e:
        logger.error(f"Database error while fetching applicants: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applicants from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching applicants: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/{applicant_id}", response_model=ApplicantResponse)
def get_applicant(applicant_id: int):
    """
    Get a specific applicant by ID
    
    - **applicant_id**: The ID of the applicant to retrieve
    """
    try:
        applicant = applicant_services.get_applicant_by_id(applicant_id)
        return applicant
    except ApplicantNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while fetching applicant {applicant_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applicant from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching applicant {applicant_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
def create_applicant(applicant: ApplicantCreate):
    """
    Create a new applicant
    
    - **name**: First name of the applicant (required)
    - **last_name**: Last name of the applicant (required)
    - **email**: Email address (required, must be valid)
    - **schedule_date**: Scheduled date (optional)
    - **min_date**: Minimum date (optional)
    - **max_date**: Maximum date (optional)
    - **schedule**: Schedule information (optional)
    """
    try:
        created_applicant = applicant_services.create_applicant(applicant)
        return created_applicant
    except DatabaseException as e:
        logger.error(f"Database error while creating applicant: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create applicant in database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while creating applicant: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/{applicant_id}", response_model=ApplicantResponse)
def update_applicant(applicant_id: int, applicant: ApplicantUpdate):
    """
    Update an existing applicant
    
    - **applicant_id**: The ID of the applicant to update
    - All fields are optional - only provided fields will be updated
    """
    try:
        updated_applicant = applicant_services.update_applicant(applicant_id, applicant)
        return updated_applicant
    except ApplicantNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while updating applicant {applicant_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update applicant in database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while updating applicant {applicant_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/{applicant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_applicant(applicant_id: int):
    """
    Delete an applicant
    
    - **applicant_id**: The ID of the applicant to delete
    """
    try:
        applicant_services.delete_applicant(applicant_id)
        return None
    except ApplicantNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except DatabaseException as e:
        logger.error(f"Database error while deleting applicant {applicant_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete applicant from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error while deleting applicant {applicant_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/{applicant_id}/test-credentials")
def test_applicant_credentials(applicant_id: int):
    """
    Test applicant credentials using Selenium and extract schedule number
    
    - **applicant_id**: The ID of the applicant to test
    
    Returns:
        - success: Whether login was successful
        - schedule: Extracted schedule number (if found)
        - error: Error message (if any)
    """
    try:
        # Get an applicant to retrieve email and password
        applicant = applicant_services.get_applicant_with_password(applicant_id)
        email = applicant.get('email')
        password = applicant.get('password')
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Applicant email or password not found"
            )
        
        # Test credentials using Selenium
        logger.info(f"Testing credentials for applicant {applicant_id}")
        result = applicant_web_services.test_credentials(email, decrypt_password(password))
        
        # If successful and schedule number found, update applicant
        if result["success"] and result["schedule"]:
            logger.info(f"Updating applicant {applicant_id} with schedule {result['schedule']}")
            applicant_services.update_applicant_schedule(applicant_id, result["schedule"])
        
        return result
    except ApplicantNotFoundException as e:
        logger.error(f"Applicant not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing credentials: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test credentials: {str(e)}"
        )
