from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.authentication import roles_required
from src.core.utils import normalize_string,hash_password
from src.models.personal import EmployeeOnboarding
from src.core.authentication import get_current_employee, get_current_employee_roles
from src.schemas.personal import  EmployeeUpdate
from src.schemas.leave import  LeaveCalendarUpdate
from src.crud.personal import (
    get_employee,
    update_employee,
)


from src.crud.employee import (
    create_employee_employment_details,
    update_employee_employment_details,
    delete_employee_employment_details,
    get_all_employee_employment_details,

)
from src.schemas.employee import (
    EmployeeEmploymentDetailsCreate,
    EmployeeEmploymentDetailsUpdate,
)
from src.crud.leave import (
 
    delete_employee_leave,
    get_leave_by_employee_id,
    get_employee_leave_by_month,
    get_leave_by_id,
    leave_calender,
    update_leave_calendar,
    get_calender_admin
)



#personal
router = APIRouter(
    prefix="/admin", tags=["admin"], responses={400: {"message": "Not found"}}
)


@router.get(
    "/personal/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
async def read_employee_route(
    employee_id: str = Path(...),db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        db_employee = get_employee(db,employee_id)
        print(db_employee)
        return db_employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")



@router.put(
    "/employees/{employee_id}",
    dependencies=[Depends(roles_required( "admin"))],
)
async def update_employee_data(
    employee_update: EmployeeUpdate,
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id_c = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db).name.lower()
    
    if employee_role == "admin":
        updated_employee = update_employee(db, employee_id, employee_update)
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    if updated_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return updated_employee



@router.delete(
    "/employees/{employee_id}", dependencies=[Depends(roles_required("admin"))]
)
async def delete_employee_route(employee_id: str, db: Session = Depends(get_db)):
    db_employee = delete_employee_employment_details(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"details": "employee deleted successfully"}


@router.post("/employees/", dependencies=[Depends(roles_required("admin"))])
async def create_employee(
    employee_employment: EmployeeEmploymentDetailsCreate, db: Session = Depends(get_db)
):
    employee_employment.job_position = normalize_string(employee_employment.job_position)
    employee_employment.department = normalize_string(employee_employment.department)
    employee_employment.email=normalize_string(employee_employment.email)
    employee_employment.password=hash_password(employee_employment.password)
    employee_employment.start_date = employee_employment.start_date
    employee_employment.employment_type = normalize_string(employee_employment.employment_type)
    employee_employment.work_location = normalize_string(
        employee_employment.work_location
    )
    employee_employment.basic_salary = employee_employment.basic_salary
    return create_employee_employment_details(db, employee_employment)

@router.get(
    "/employees/{employee_id}",
    dependencies=[Depends(roles_required( "admin"))],
)
async def read_employee(
    employee_id: str = Path(...),  # Path parameter is required, but use a placeholder
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)

    if employee_role.name == "admin":
        db_employee = get_all_employee_employment_details(db, employee_id)
    

    # Prepare the response with employee details
        employee_details = {
            "employee_email": db_employee.employee_email,
            "job_position": db_employee.job_position,
            "department": db_employee.department,
            "start_date": db_employee.start_date,
            "employment_type": db_employee.employment_type,
            "reporting_manager": db_employee.reporting_manager,
            "work_location": db_employee.work_location,
            "basic_salary": db_employee.basic_salary,
            "is_active": db_employee.is_active,
            "releave_date": str(db_employee.releave_date),
            "employee_data":db_employee.employee.employment_id,
            "employee_name":db_employee.employee.firstname
        }

        return employee_details

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")


@router.put("/employees/update/admin", dependencies=[Depends(roles_required("admin"))])
async def update_employee_admin(
    employee_update: EmployeeEmploymentDetailsUpdate, db: Session = Depends(get_db)
):
    db_employee = update_employee_employment_details(db, employee_update)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@router.delete(
    "/employees/{employee_id}", dependencies=[Depends(roles_required("admin"))]
)
async def delete_employee_details(employee_id: str, db: Session = Depends(get_db)):
    db_employee = delete_employee_employment_details(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "The Employee is Deleted Successfully"}


@router.get(
    "/pending/leave/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
def get_leave_by(
    employee_id: str = Path(...),db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        db_leave = get_leave_by_id(db,employee_id)
    if not db_leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    leave_details = [
        {"employee_id": leave.employee.employee_id, "leave_id": leave.id}
        for leave in db_leave
    ]

    return leave_details

@router.get(
    "/{monthnumber}/{yearnumber}/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
def get_leave_by_month(
    monthnumber: int,
    yearnumber: int,
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee: EmployeeOnboarding = Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        return get_employee_leave_by_month(db, employee_id, monthnumber, yearnumber)
    return {"detail": "No leaves this Month"}


@router.get(
    "/leaves/{employee_id}", dependencies=[Depends(roles_required("employee", "teamlead", "admin"))]
)
def get_leaves_by_employee(
    employee_id: str = Path(...),  # Declare as an optional query parameter
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        db_employee = get_leave_by_employee_id(db, employee_id)
    if not employee_role.name=="admin":
        raise HTTPException(status_code=404, detail="Not Authorized for this action ")
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not applied for leave")
    return db_employee


@router.delete(
    "/{leave_id}",
    dependencies=[Depends(roles_required("admin"))],
)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_employee),
):
    success = delete_employee_leave(db, current_user.id, leave_id)
    if not success:
        raise HTTPException(status_code=404, detail="Leave not found")
    return {"leave deleted successfully"}


@router.put("/update/leave/calender/",dependencies=[Depends(roles_required("admin"))])
async def update_leave( leave_update: LeaveCalendarUpdate, db: Session = Depends(get_db)):
    # Update the leave calendar entry
    return update_leave_calendar(db, leave_update)

@router.post("/calender", dependencies=[Depends(roles_required("admin"))])
async def create_leave_calendar(db: Session = Depends(get_db)):
    return leave_calender(db)


@router.get("/calender/{employee_id}", dependencies=[Depends(roles_required("admin"))])
async def get_leave_calendar(employee_id:str ,db: Session = Depends(get_db)):
    return get_calender_admin(db,employee_id)


# Inserted class definitions
from pydantic import BaseModel, validator, Field, EmailStr
from dateutil import parser
from typing import Optional
from datetime import date

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

# Inserted class definitions
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date, datetime


class LeaveDuration(str, Enum):
    ONE_DAY = "oneday"
    HALF_DAY = "halfday"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveCalendarUpdate(BaseModel):
    employee_id: str
    sick_leave: Optional[int] = None
    personal_leave: Optional[int] = None
    vacation_leave: Optional[int] = None

# Inserted class definitions
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