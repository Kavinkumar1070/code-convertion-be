from datetime import datetime  # Change here to import datetime instead of date
from typing import Optional
from dateutil import parser
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator

class EmployeeBase(BaseModel):
    firstname: str
    lastname: str
    dateofbirth: str
    contactnumber: int
    emailaddress: EmailStr
    address: str
    nationality: str
    gender: str
    maritalstatus: str

    @field_validator("contactnumber")
    def validate_phone_number(cls, value):
        contact_number_str = str(value)
        if len(contact_number_str) != 10:
            raise ValueError("Invalid phone number length. Phone number must be 10 digits.")
        return value

    @field_validator("dateofbirth", mode="before")
    def parse_date(cls, value):
        if value is not None:
            # Define possible formats to check
            formats = [
                "%Y-%m-%d",  # YYYY-MM-DD
                "%d/%m/%Y",  # DD/MM/YYYY
                "%m/%d/%Y",  # MM/DD/YYYY
                "%Y/%m/%d",  # YYYY/MM/DD
            ]

            for fmt in formats:
                try:
                    # Use datetime to parse
                    parsed_date = datetime.strptime(value, fmt)
                    return parsed_date.strftime("%Y-%m-%d")  # Convert to standard format
                except ValueError:
                    continue  # Try the next format

            # If none of the formats worked, fall back to dateutil.parser
            try:
                parsed_date = parser.parse(value)
                return parsed_date.strftime("%Y-%m-%d")  # Convert to standard format
            except (ValueError, TypeError):
                raise ValueError("Invalid date format. Please use a valid date string.")
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    dateofbirth: Optional[str] = Field(None, example="1990-05-15")
    contactnumber: Optional[str] = None
    emailaddress: Optional[EmailStr] = None
    address: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    maritalstatus: Optional[str] = None

    @field_validator("dateofbirth", mode="before")
    def parse_date(cls, value):
        if value is not None:
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%Y/%m/%d",
            ]

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(value, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            try:
                parsed_date = parser.parse(value)
                return parsed_date.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                raise ValueError("Invalid date format. Please use a valid date string.")
        return value
