from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.core.authentication import (get_current_employee,
                                     get_current_employee_roles,
                                     roles_required)
from src.core.database import SessionLocal
from src.core.utils import hash_password, normalize_string, send_email
from src.crud.personal import create_employee, get_employee, update_employee
from src.models.personal import EmployeeOnboarding
from src.schemas.personal import EmployeeCreate, EmployeeUpdate

router = APIRouter(
    prefix="/personal", tags=["Personal"], responses={400: {"detail": "Not found"}}
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect date format. Use YYYY-MM-DD.",
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
    # Ensure create_employee is synchronous
    details = create_employee(db, employee)

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
        db_employee = get_employee(db, current_employee_id)
        return db_employee

    if employee_role.name == "teamlead":
        db_employee = get_employee(db, current_employee_id)
        return db_employee
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{current_employee_id}' is  not found",
        )


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
    employee_role = get_current_employee_roles(
        current_employee.id, db).name.lower()

    # Perform update based on role
    if employee_role in ["employee", "teamlead"]:
        updated_employee = update_employee(db, employee_id_c, employee_update)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unauthorized Role to Access this Route",
        )
    if updated_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id_c}' is not found",
        )

    return updated_employee