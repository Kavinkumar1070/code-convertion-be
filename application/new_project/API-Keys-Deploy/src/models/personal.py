from datetime import datetime

from sqlalchemy import (BigInteger, Column, Date, DateTime, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from src.core.database import Base

from .association import employee_role


class EmployeeOnboarding(Base):
    __tablename__ = "employee_onboarding"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employment_id = Column(String(100), unique=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    dateofbirth = Column(Date, nullable=False)
    contactnumber = Column(BigInteger, nullable=False)
    emailaddress = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    nationality = Column(String(50), nullable=False)
    gender = Column(String(10))
    maritalstatus = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    employment_details = relationship(
        "EmployeeEmploymentDetails", back_populates="employee"
    )
    roles = relationship(
        "Role",
        secondary=employee_role,
        back_populates="employees")
