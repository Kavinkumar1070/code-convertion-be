from typing import Optional

from pydantic import BaseModel, validator


class RoleCreate(BaseModel):
    name: str
    sick_leave: int
    personal_leave: int
    vacation_leave: int

    class Config:
        from_attributes = True

    @validator("sick_leave")
    def number_validator(cls, value):
        if value <= 0:
            raise ValueError("Leave values must be greater than 0")
        return value


class UpdateRole(BaseModel):
    role_id: int
    new_name: Optional[str] = None
    sick_leave: Optional[int] = None
    personal_leave: Optional[int] = None
    vacation_leave: Optional[int] = None

    @validator("sick_leave", "personal_leave",
               "vacation_leave", pre=True, always=True)
    def leave_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Leave values must be greater than 0")
        return v


class EmployeeRole(BaseModel):
    employee_id: str
    role_id: int


class RoleFunctionCreate(BaseModel):
    role_id: int
    function: str
    jsonfile: str


class UpateRoleFunction(BaseModel):
    function_id: int
    function: Optional[str] = None
    jsonfile: Optional[str] = None
