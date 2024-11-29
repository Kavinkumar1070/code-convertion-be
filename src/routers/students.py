from fastapi import APIRouter, Depends, HTTPException, status
from src.core.database import get_db
from sqlalchemy.orm import Session
from src.models.students import Students
from typing import List
from src.schemas.students import StudentCreate,StudentResponse,UpdateStudent
from src.repositories.students import create_student, get_student, get_students, update_student, delete_student

router = APIRouter()

@router.post("/students/", response_model=StudentResponse)
def create_new_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = create_student(db=db, student=student)
    if not db_student:
        raise HTTPException(status_code=400, detail="Student creation failed")
    return db_student
@router.get("/students/{student_id}",response_model=StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = get_student(db=db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/students/",response_model=List[StudentResponse])
def read_students(db: Session = Depends(get_db)):
    return get_students(db=db)

@router.put("/students/{student_id}",response_model=StudentResponse)
def update_existing_student(student_id: int, student: UpdateStudent, db: Session = Depends(get_db)):
    return update_student(db=db, student_id=student_id, student=student)

@router.delete("/students/{student_id}")
def delete_existing_student(student_id: int, db: Session = Depends(get_db)):
    return delete_student(db=db, student_id=student_id)


# Inserted class definitions
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date

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