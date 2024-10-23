from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.core.database import Base

from .association import employee_role


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    sick_leave = Column(Integer, default=0)
    personal_leave = Column(Integer, default=0)
    vacation_leave = Column(Integer, default=0)
    employees = relationship(
        "EmployeeOnboarding", secondary=employee_role, back_populates="roles"
    )
    functions = relationship(
        "RoleFunction", back_populates="role", cascade="all, delete-orphan"
    )


# Function model
class RoleFunction(Base):
    __tablename__ = "role_function"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    function = Column(String(500), index=True)
    jsonfile = Column(String(80), index=True)

    role = relationship("Role", back_populates="functions")
