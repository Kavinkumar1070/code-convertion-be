from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.core.authentication import (get_current_employee,
                                     get_current_employee_roles,
                                     roles_required)
from src.core.database import get_db
from src.core.utils import send_email_leave
from src.crud.leave import (create_employee_leave, delete_employee_leave,
                            get_calender, get_calender_tl,
                            get_employee_leave_by_month,
                            get_employee_leave_by_month_tl, get_leave_by_admin,
                            get_leave_by_employee_id,
                            get_leave_by_employee_team, get_leave_by_id,
                            get_leave_by_report_manager, leave_calender,
                            update_employee_leave, update_employee_teamlead,get_employee_tl,
                            update_leave_calendar)
from src.models.leave import LeaveCalendar
from src.models.personal import EmployeeOnboarding
from src.schemas.leave import (EmployeeLeaveCreate, EmployeeLeaveUpdate,
                               LeaveCalendarUpdate)

router = APIRouter(
    prefix="/leave", tags=["leave"], responses={400: {"detail": "Not found"}}
)


@router.post(
    "/", dependencies=[Depends(roles_required("employee", "admin", "teamlead"))]
)
async def apply_leave(
    leave: EmployeeLeaveCreate,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    # Ensure this is the correct type
):
    # Accessing employee_id directly from the object
    employee_id = current_employee.employment_id
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Employee data Please Authenticate ",
        )
    db_leave = create_employee_leave(db, leave, employee_id)
    email_leav = db_leave["employee_email"]
    await send_email_leave(
        db_leave["employee_email"],
        db_leave["employee_firstname"],
        db_leave["employee_lastname"],
        db_leave["leave"],
        db_leave["reason"],
        db_leave["status"],
        db_leave["other_entries"],
    )
    return {
        "details": f"leave applied successfully for '{employee_id}' check your mail '{email_leav}'"
    }


@router.get("/details",
            dependencies=[Depends(roles_required("employee", "teamlead"))])
def get_leaves_by_employee(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db).name

    # Determine employee to fetch leave details for
    if employee_role == "employee" or employee_role == "teamlead":
        db_employee = get_leave_by_employee_id(db, current_employee_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee id :{current_employee_id.employee_id} not found",
        )

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{current_employee_id}' not applied for leave",
        )

    return db_employee


@router.get(
    "/pending/leave",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
def get_leave_by(
    db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "employee":
        db_leave = get_leave_by_id(db, current_employee_id)
    if employee_role.name == "teamlead":
        db_leave = get_leave_by_id(db, current_employee_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{current_employee_id}' has no pending leaves",
        )
    leave_details = [
        { "leave_id": leave.id,"employee_id": leave.employee.employee_id ,"leave_type":leave.leave_type,"Reason":leave.reason}
        for leave in db_leave
    ]

    return leave_details


@router.get(
    "/pending/leave/all",
    dependencies=[Depends(roles_required("teamlead"))],
)
def get_leave_of_employee(
    db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "teamlead":
        db_leave = get_leave_by_report_manager(db, current_employee_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{current_employee_id.employee_id}' has no pending leaves",
        )
    leave_details = [
        {
            "leave_id": leave.id,
            "employee_id": leave.employee.employee_id,
            "Leave Type": leave.leave_type,
            "date": leave.start_date,
            "Reason": leave.reason,
        }
        for leave in db_leave
    ]
    return leave_details


@router.get(
    "/{monthnumber}/{yearnumber}",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
def get_leave_by_month(
    monthnumber: int,
    yearnumber: int,
    db: Session = Depends(get_db),
    current_employee: EmployeeOnboarding = Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "employee":
        return get_employee_leave_by_month(
            db, current_employee_id, monthnumber, yearnumber
        )

    if employee_role.name == "teamlead":
        return get_employee_leave_by_month(
            db, current_employee_id, monthnumber, yearnumber
        )
    return {"detail": f" No leaves Applied for This Month to '{current_employee_id}' "}


@router.put(
    "/admin/teamlead/update",
    dependencies=[Depends(roles_required("teamlead", "admin"))],
)
async def update_leave(
    leave: EmployeeLeaveUpdate,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    report_manager = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        if leave.status == "approved":
            db_leave = update_employee_leave(db, leave)
        elif leave.status == "rejected":
            if not leave.reason or not leave.reason.strip():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Please provide a reason for rejecting the leave.",
                )
            db_leave = update_employee_leave(db, leave)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid leave status provided 'Pending'.",
            )
    if employee_role.name == "teamlead":
        if leave.status == "approved":
            db_leave = update_employee_teamlead(db, report_manager, leave)
        elif leave.status == "rejected":
            if not leave.reason or not leave.reason.strip():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Please provide a reason for rejecting the leave.",
                )
            db_leave = update_employee_teamlead(db, report_manager, leave)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid leave status provided 'Pending'.",
            )

    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found {leave.leave_id}",
        )
    await send_email_leave(
        db_leave["employee_email"],
        db_leave["employee_firstname"],
        db_leave["employee_lastname"],
        db_leave["leave"],
        db_leave["reason"],
        db_leave["status"],
        db_leave["other_entires"],
    )
    return db_leave


@router.delete(
    "/{leave_id}",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_employee),
):
    success = delete_employee_leave(db, current_user.id, leave_id)
    return {"leave deleted successfully"}


@router.get("/calender",
            dependencies=[Depends(roles_required("employee", "teamlead"))])
async def get_leave_calendar(
    db: Session = Depends(get_db), current_employee=Depends(get_current_employee)
):
    employee_id = current_employee.id
    return get_calender(db, employee_id)


@router.get(
    "/teamlead/calender/{employee_id}",
    dependencies=[Depends(roles_required("teamlead"))],
)
async def get_leave_calendar_tl(
    employee_id: str = Path(...),
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    report_manager = current_employee.employment_id
    return get_calender_tl(db, report_manager, employee_id)


@router.get(
    "/teamlead/employee/",
    dependencies=[Depends(roles_required("admin","teamlead"))],
)
async def get_employee_under_tl(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    report_manager = current_employee.employment_id
    
    data= get_employee_tl(db, report_manager)
    datas = [
            {
                    "employee_id":details.employee_id,
                    "first_name": details.employee.firstname,
                    "department":details.department,
                    "job_position":details.job_position,
                    "is_active": details.is_active,
                    
                    
                    

            }
            for details in data
        ]
        
    return datas