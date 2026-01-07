"""Custom exceptions for NextVisa API"""

class ApplicantNotFoundException(Exception):
    """Raised when an applicant is not found in the database"""
    def __init__(self, applicant_id: int):
        self.applicant_id = applicant_id
        self.message = f"Applicant with ID {applicant_id} not found"
        super().__init__(self.message)


class DuplicateApplicantException(Exception):
    """Raised when attempting to create a duplicate applicant"""
    def __init__(self, email: str):
        self.email = email
        self.message = f"Applicant with email {email} already exists"
        super().__init__(self.message)


class DatabaseException(Exception):
    """Raised when a database operation fails"""
    def __init__(self, operation: str, details: str = ""):
        self.operation = operation
        self.details = details
        self.message = f"Database operation '{operation}' failed"
        if details:
            self.message += f": {details}"
        super().__init__(self.message)
