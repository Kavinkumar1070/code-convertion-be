from datetime import date, datetime
from enum import Enum
from typing import Optional

from dateutil import parser
from pydantic import BaseModel, Field, validator


class LeaveDuration(str, Enum):
    ONE_DAY = "oneday"
    HALF_DAY = "halfday"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmployeeLeaveBase(BaseModel):
    leave_type: str
    duration: LeaveDuration
    start_date: date
    total_days: int = Field(gt=0)
    reason: Optional[str] = None

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


class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass


class EmployeeLeaveUpdate(BaseModel):
    leave_id: int
    status: LeaveStatus
    reason: Optional[str] = None


class EmployeeLeaveResponse(BaseModel):
    id: int
    employee_id: int
    report_manager_id: int
    leave_type: str
    duration: LeaveDuration
    start_date: date
    end_date: date
    status: LeaveStatus
    reason: Optional[str] = None
    reject_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

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

    class Config:
        orm_mode = True


class LeaveCalendarUpdate(BaseModel):
    employee_id: str
    sick_leave: Optional[int] = None
    personal_leave: Optional[int] = None
    vacation_leave: Optional[int] = None
