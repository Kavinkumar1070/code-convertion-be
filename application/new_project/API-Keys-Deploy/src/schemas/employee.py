from datetime import date
from typing import Optional

from dateutil import parser
from pydantic import BaseModel, EmailStr, field_validator


class EmployeeEmploymentDetailsBase(BaseModel):
    employment_id: str
    job_position: str
    email: EmailStr
    password: str
    department: str
    start_date: date
    employment_type: str
    reporting_manager: Optional[str]
    work_location: Optional[str]
    basic_salary: Optional[float]

    @field_validator("start_date", mode="before")
    def parse_date(cls, value):
        if value is not None:
            try:
                # Parse the date from various formats
                parsed_date = parser.parse(value)
                return parsed_date.date()  # Return as date object
            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid date format. Please use a valid date string."
                )
        return value


class EmployeeEmploymentDetailsCreate(EmployeeEmploymentDetailsBase):
    pass


class EmployeeEmploymentDetailsUpdate(BaseModel):
    employment_id: str = "cds0001"
    job_position: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    employment_type: Optional[str] = None
    reporting_manager: Optional[str] = None
    work_location: Optional[str] = None
    employee_email: Optional[EmailStr] = None
    basic_salary: Optional[float] = None

    @field_validator("start_date", mode="before")
    def parse_date(cls, value):
        if value is not None:
            try:
                # Parse the date from various formats
                parsed_date = parser.parse(value)
                return parsed_date.date()  # Return as date object
            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid date format. Please use a valid date string."
                )
        return value


class EmployeeEmploymentDetails(EmployeeEmploymentDetailsBase):
    id: int

    class Config:
        from_attributes = True  # Updated from 'orm_mode' to 'from_attributes'


class Login(BaseModel):
    email: str
    password: str
