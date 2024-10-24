from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class EmployeeEmploymentDetailsBase(BaseModel):
    employment_id: str
    job_position: str
    email:EmailStr
    password:str
    department: str
    start_date: date
    employment_type: str
    reporting_manager: Optional[str]
    work_location: Optional[str]
    basic_salary: Optional[float]


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


class EmployeeEmploymentDetails(EmployeeEmploymentDetailsBase):
    id: int
    employment_id: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: str
    password: str
    
from enum import Enum
from pydantic import AnyUrl, BaseModel, EmailStr, Field
 
 
class MusicBand(str, Enum):
   AEROSMITH = "AEROSMITH"
   QUEEN = "QUEEN"
   ACDC = "AC/DC"
 
 
class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128, pattern="^[A-Za-z0-9-_]+$")
    email: EmailStr
    age: int = Field(ge=18, default=None)  # must be greater or equal to 18
    favorite_band: MusicBand | None = None  # only "AEROSMITH", "QUEEN", "AC/DC" values are allowed to be inputted
    website: AnyUrl | None = None
