from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.core.authentication import (get_current_employee,
                                     get_current_employee_roles,
                                     roles_required)
from src.core.database import get_db
from src.core.utils import hash_password, normalize_string
from src.crud.employee import (create_employee_employment_details,
                               delete_employee_employment_details,
                               get_all_employee_employment_details,
                               update_employee_employment_details)
from src.crud.leave import (delete_employee_leave, get_calender_admin,
                            get_employee_leave_by_month,
                            get_leave_by_employee_id, get_leave_by_id,
                            leave_calender, update_leave_calendar)
from src.crud.personal import get_employee, update_employee
from src.models.personal import EmployeeOnboarding
from src.schemas.employee import (EmployeeEmploymentDetailsCreate,
                                  EmployeeEmploymentDetailsUpdate)
from src.schemas.leave import LeaveCalendarUpdate
from src.schemas.personal import EmployeeUpdate

# personal
router = APIRouter(
    prefix="/admin", tags=["admin"], responses={400: {"detail": "Not found"}}
)


@router.get(
    "/personal/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
async def read_employee_route(
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        db_employee = get_employee(db, employee_id)
        print(db_employee)
        return db_employee
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee Id:{employee_id} not found",
        )


@router.put(
    "/employees/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
async def update_employee_data(
    employee_update: EmployeeUpdate,
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id_c = current_employee.employment_id
    employee_role = get_current_employee_roles(
        current_employee.id, db).name.lower()

    if employee_role == "admin":
        updated_employee = update_employee(db, employee_id, employee_update)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unauthorized role Only Admin can Access",
        )

    if updated_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee Id:{employee_id} not found",
        )

    return updated_employee


@router.delete(
    "/employees/{employee_id}", dependencies=[Depends(roles_required("admin"))]
)
async def delete_employee_route(
        employee_id: str, db: Session = Depends(get_db)):
    db_employee = delete_employee_employment_details(db, employee_id)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee Id:{employee_id} not found",
        )
    return {"details": f"employee {employee_id} deleted successfully"}


@router.post("/employees/", dependencies=[Depends(roles_required("admin"))])
async def create_employee(
    employee_employment: EmployeeEmploymentDetailsCreate, db: Session = Depends(get_db)
):
    employee_employment.job_position = normalize_string(
        employee_employment.job_position
    )
    employee_employment.department = normalize_string(
        employee_employment.department)
    employee_employment.email = normalize_string(employee_employment.email)
    employee_employment.password = hash_password(employee_employment.password)
    employee_employment.start_date = employee_employment.start_date
    employee_employment.employment_type = normalize_string(
        employee_employment.employment_type
    )
    employee_employment.work_location = normalize_string(
        employee_employment.work_location
    )
    employee_employment.basic_salary = employee_employment.basic_salary
    return create_employee_employment_details(db, employee_employment)


@router.get(
    "/employees/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
async def read_employee(
    # Path parameter is required, but use a placeholder
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)

    if employee_role.name == "admin":
        db_employee = get_all_employee_employment_details(db, employee_id)

        # Prepare the response with employee details
        employee_details = {
            "id": db_employee.id,
            "employee_data": db_employee.employee.employment_id,
            "employee_name": db_employee.employee.firstname,
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
        }

        return employee_details

    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee Id:{employee_id} not found",
        )


@router.put("/employees/update/admin",
            dependencies=[Depends(roles_required("admin"))])
async def update_employee_admin(
    employee_update: EmployeeEmploymentDetailsUpdate, db: Session = Depends(get_db)
):
    db_employee = update_employee_employment_details(db, employee_update)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee Id:{employee_update.employment_id} not found",
        )
    return db_employee


@router.delete(
    "/employees/{employee_id}", dependencies=[Depends(roles_required("admin"))]
)
async def delete_employee_details(
        employee_id: str, db: Session = Depends(get_db)):
    db_employee = delete_employee_employment_details(
        db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return {"detail": f"The Employee '{employee_id}' is Deleted Successfully"}


@router.get(
    "/pending/leave/{employee_id}",
    dependencies=[Depends(roles_required("admin"))],
)
def get_leave_by(
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        db_leave = get_leave_by_id(db, employee_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Pending Leave for this Employee {employee_id}",
        )
    leave_details = [
        {
            "leave_id": leave.id,
            "employee_id": leave.employee.employee_id,
            "date": leave.start_date,
            "Reason": leave.leave_type,
        }
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
        data = get_employee_leave_by_month(
            db, employee_id, monthnumber, yearnumber)
        if not data:
            return {
                "detail": f"There is  No leaves this Month for Employee {employee_id}"
            }
        return data


@router.get(
    "/leaves/{employee_id}",
    dependencies=[Depends(roles_required("employee", "teamlead", "admin"))],
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
    if not employee_role.name == "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Authorized for this action ",
        )
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} not applied for leave",
        )
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave id '{leave_id}' not found",
        )
    return {"details": f"leave id :{leave_id} deleted successfully"}


@router.put("/update/leave/calender/",
            dependencies=[Depends(roles_required("admin"))])
async def update_leave(
    leave_update: LeaveCalendarUpdate, db: Session = Depends(get_db)
):
    # Update the leave calendar entry
    return update_leave_calendar(db, leave_update)


@router.post("/calender", dependencies=[Depends(roles_required("admin"))])
async def create_leave_calendar(db: Session = Depends(get_db)):
    return leave_calender(db)


@router.get("/calender/{employee_id}",
            dependencies=[Depends(roles_required("admin"))])
async def get_leave_calendar(employee_id: str, db: Session = Depends(get_db)):
    return get_calender_admin(db, employee_id)
