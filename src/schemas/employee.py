from datetime import date
from typing import Optional

from dateutil import parser
from pydantic import BaseModel, EmailStr, validator


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

    @validator("start_date", pre=True)
    def parse_date(cls, value):
        if value is not None:
            try:
                # Parse the date from various formats
                parsed_date = parser.parse(value)
                return parsed_date.strftime(
                    "%Y-%m-%d"
                )  # Convert to standard format YYYY-MM-DD
            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid date format. Please use a valid date string.")
        return value


class EmployeeEmploymentDetailsCreate(EmployeeEmploymentDetailsBase):
    pass


class EmployeeEmploymentDetailsUpdate(BaseModel):
    employment_id: str = "cds0001"
    job_position: str | None = None
    department: str | None = None
    start_date: date | None = None
    employment_type: str | None = None
    reporting_manager: Optional[str] = None
    work_location: Optional[str] = None
    employee_email: Optional[EmailStr] = None
    basic_salary: Optional[float] = None

    @validator("start_date", pre=True)
    def parse_date(cls, value):
        if value is not None:
            try:
                # Parse the date from various formats
                parsed_date = parser.parse(value)
                return parsed_date.strftime(
                    "%Y-%m-%d"
                )  # Convert to standard format YYYY-MM-DD
            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid date format. Please use a valid date string.")
        return value


class EmployeeEmploymentDetails(EmployeeEmploymentDetailsBase):
    id: int
    employment_id: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: str
    password: str
