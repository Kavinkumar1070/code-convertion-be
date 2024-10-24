from datetime import date, datetime

from sqlalchemy import (DECIMAL, Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, String, func)
from sqlalchemy.orm import relationship, validates

from src.core.database import Base


class EmployeeEmploymentDetails(Base):
    __tablename__ = "employee_employment_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_email = Column(String(100), unique=True)
    password = Column(String(100), unique=True)
    job_position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    employment_type = Column(String(50), nullable=False)
    reporting_manager = Column(String(20))
    work_location = Column(String(100))
    basic_salary = Column(DECIMAL(10, 2))
    releave_date = Column(Date, default=None)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    # Ensure that the type of employee_id matches the type of employment_id in
    # EmployeeOnboarding
    employee_id = Column(String(100), ForeignKey(
        "employee_onboarding.employment_id"))
    employee = relationship(
        "EmployeeOnboarding",
        back_populates="employment_details")
    leaves = relationship("EmployeeLeave", back_populates="employee")
    leave_calendar = relationship(
        "LeaveCalendar", uselist=False, back_populates="employee"
    )
    chathistory = relationship("ChatHistory",back_populates="employee")

    @validates("is_active")
    def validate_is_active(self, key, value):
        if not value:
            self.releave_date = date.today()
        return value
