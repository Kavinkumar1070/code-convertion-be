from fastapi import APIRouter, Depends, HTTPException,Path
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.personal import EmployeeOnboarding
from src.core.authentication import get_current_employee, get_current_employee_roles
from src.crud.personal import (
    create_employee,
    get_employee,
    update_employee,
)
from src.schemas.personal import EmployeeCreate, EmployeeUpdate
from src.core.utils import normalize_string, send_email,hash_password
from src.core.authentication import roles_required
from datetime import datetime,date

router = APIRouter(
    prefix="/personal", tags=["Personal"], responses={400: {"message": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def convert_date_format(date_input):
    # Check if the input is already a date object
    if isinstance(date_input, date):
        return date_input.strftime("%Y-%m-%d")
    
    # If the input is a string, try to parse it
    try:
        date_obj = datetime.strptime(date_input, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Incorrect date format. Use YYYY-MM-DD."
        )


@router.post("/employees")
async def create_employee_route(
    employee: EmployeeCreate, db: Session = Depends(get_db)
):
    # Normalize strings
    employee.firstname = normalize_string(employee.firstname)
    employee.lastname = normalize_string(employee.lastname)
    employee.address = normalize_string(employee.address)
    employee.dateofbirth = convert_date_format(employee.dateofbirth)
    employee.nationality = normalize_string(employee.nationality)
    employee.gender = normalize_string(employee.gender)
    employee.maritalstatus = normalize_string(employee.maritalstatus)
    employee.emailaddress = normalize_string(employee.emailaddress)

    # Create employee and get details
    details = create_employee(db, employee)  # Ensure create_employee is synchronous

    # Send the email asynchronously
    await send_email(
        recipient_email=details["emailaddress"],
        name=details["firstname"],
        lname=details["lastname"],
        Email=details["employee_email"],
        Password=details["password"],
    )

    return {"detail": "Email Send Successfully"}


@router.get(
    "/employees",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
async def read_employee_route(
    db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "employee":
        db_employee = get_employee(db,current_employee_id)
        return db_employee
    if employee_role.name == "teamlead":
            db_employee = get_employee(db,current_employee_id)
            return db_employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@router.put(
    "/employees",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
async def update_employee_data(
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id_c = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db).name.lower()
    
    # Perform update based on role
    if employee_role in ["employee", "teamlead"]:
        updated_employee = update_employee(db, employee_id_c, employee_update)
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")
    if updated_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return updated_employee




# Inserted class definitions
from pydantic import BaseModel, validator, Field, EmailStr
from dateutil import parser
from datetime import date
from typing import Optional


class EmployeeBase(BaseModel):
    firstname: str
    lastname: str
    dateofbirth: str 
    contactnumber: int
    emailaddress: EmailStr
    address: str
    nationality: str
    gender: str
    maritalstatus: str

    @validator("contactNumber", check_fields=False)
    def validate_phone_number(cls, value):
        contact_number_str = str(value)
        if not (10 == len(contact_number_str)):
            raise ValueError(
                "Invalid phone number length. Phone number must be between 9 and 12 digits."
            )
        return value

    @validator('dateofbirth', pre=True)
    def parse_date(cls, value):
        try:
            # Parse the date from various formats
            parsed_date = parser.parse(value)
            return parsed_date.strftime('%Y-%m-%d')  # Convert to standard format YYYY-MM-DD
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Please use a valid date string.")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    dateofbirth: Optional[str] = Field(None, example="1990-05-15")
    contactnumber: Optional[int] = None
    emailaddress: Optional[EmailStr] = None
    address: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    maritalstatus: Optional[str] = None

    @validator("contactnumber", check_fields=False)
    def validate_phone_number(cls, value):
        if value is None:
            return value  # Skip validation if the value is None
    @validator('dateofbirth', pre=True)
    def parse_date(cls, value):
        if value is not None:
            try:
                # Parse the date from various formats
                parsed_date = parser.parse(value)
                return parsed_date.strftime('%Y-%m-%d')  # Convert to standard format YYYY-MM-DD
            except (ValueError, TypeError):
                raise ValueError("Invalid date format. Please use a valid date string.")
        return value