# schemas.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date
import re

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    gender:  str
    age: int
    date_of_birth: date 
    religion:  str
    father_name:  str
    mother_name:  str
    student_email: EmailStr
    parent_email: EmailStr
    student_contact_no: int 
    father_contact_no:  int
    mother_contact_no:  Optional[int] = None
    father_occupation:  str
    mother_occupation:  str
    address:  str
    landmark:  str
    city:  str
    state:  str
    country: str   
    pincode: int
    student_image:str
    emergency_contact_name:str  
    emergency_contact_no: int 
    relationship_emergency_contact:  str
    class Config:
        orm_mode = True
    @validator('student_contact_no', 'father_contact_no', 'mother_contact_no', 'emergency_contact_no', pre=True, always=True)
    def validate_contact_no(cls, v):
        if v and len(str(v)) < 10:
            raise ValueError('Contact number must be at least 10 digits long')
        return v
    
class StudentResponse(BaseModel):
    id:int
    first_name: str
    last_name: str
    gender:  str
    age: int
    date_of_birth: date 
    religion:  str
    father_name:  str
    mother_name:  str
    student_email: EmailStr
    parent_email: EmailStr
    student_contact_no: int 
    father_contact_no:  int
    mother_contact_no:  Optional[int] = None
    father_occupation:  str
    mother_occupation:  str
    address:  str
    landmark:  str
    city:  str
    state:  str
    country: str   
    pincode: int
    emergency_contact_name:str  
    emergency_contact_no: int 
    relationship_emergency_contact:  str
    student_image:str

    class Config:
        orm_mode = True

class UpdateStudent(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    date_of_birth: Optional[date] = None
    religion: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    student_email: Optional[EmailStr] = None
    parent_email: Optional[EmailStr] = None
    student_contact_no: Optional[int] = None
    father_contact_no: Optional[int] = None
    mother_contact_no: Optional[int] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[int] = None
    student_image: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_no: Optional[int] = None
    relationship_emergency_contact: Optional[str] = None

    @validator('student_contact_no', 'father_contact_no', 'mother_contact_no', 'emergency_contact_no', pre=True, always=True)
    def validate_contact_no(cls, v):
        if v and len(str(v)) < 10:
            raise ValueError('Contact number must be at least 10 digits long')
        return v

    class Config:
        orm_mode = True