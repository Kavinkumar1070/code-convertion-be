from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import extract

from src.core.utils import normalize_string, send_email_leave
from src.models.association import employee_role
from src.models.employee import EmployeeEmploymentDetails
from src.models.leave import (EmployeeLeave, LeaveCalendar, LeaveDuration,
                              LeaveStatus)
from src.models.role import Role
from src.schemas.leave import (EmployeeLeaveCreate, EmployeeLeaveUpdate,
                               LeaveCalendarUpdate)


def adjust_leave_balance(
    db: Session,
    employee_id: int,
    employee_employment_id: str,
    leave_type: str,
    duration: str,
):
    # Define mappings for leave types and their error messages
    leave_fields = {
        "sick": (
            "sick_leave",
            "Sick leave quota is exhausted. You cannot approve additional sick leave.",
        ),
        "personal": (
            "personal_leave",
            "Personal leave quota is exhausted. You cannot approve additional personal leave.",
        ),
        "vacation": (
            "vacation_leave",
            "Vacation leave quota is exhausted. You cannot approve additional vacation leave.",
        ),
        "unpaid": (
            "unpaid_leave",
            "Unpaid leave quota is exhausted. You cannot approve additional unpaid leave.",
        ),
    }
    # Retrieve the leave calendar entry for the given employee_id
    leave_calendar = (
        db.query(LeaveCalendar).filter(
            LeaveCalendar.employee_id == employee_id).first()
    )
    if not leave_calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LeaveCalendar entry not found for the specified employee {employee_id}.",
        )
    if leave_type not in leave_fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid leave type specified. Please use 'sick', 'personal', 'vacation', or 'unpaid'.",
        )
    # Get the field name and error message from the mappings
    field_name, error_message = leave_fields[leave_type]
    # Get the current leave balance for the specified leave type
    current_balance = getattr(leave_calendar, field_name)
    # Define decrement values
    decrement_value = (
        1 if duration == "oneday" else 0.5
    )  # Decrease by 1 for oneday, 0.5 for halfday
    # Check if the employee is applying for a full day leave but only has 0.5
    # days left
    if current_balance == 0.5 and duration == "oneday":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You only have {current_balance} {leave_type} leave left. You cannot apply for a full day leave.",
        )
    # Check if the leave type is unpaid (no limit)
    if leave_type == "unpaid":
        increment_value = 1 if duration == "oneday" else 0.5
        setattr(leave_calendar, field_name, current_balance + increment_value)
        db.commit()
        db.refresh(leave_calendar)
        return leave_calendar
    # Handle other leave types (sick, personal, vacation)
    if current_balance >= decrement_value:
        setattr(leave_calendar, field_name, current_balance - decrement_value)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{error_message} Current balance: {current_balance}. You cannot apply/approve this leave.",
        )

    # Commit the transaction and handle errors
    try:
        db.commit()  # Commit the changes to the database
        # Refresh the instance to reflect updated data
        db.refresh(leave_calendar)
    except Exception as e:
        db.rollback()  # Roll back the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the leave balance.",
        )

    # Return the leave calendar with updated balances
    return {
        "employee_id": employee_employment_id,
        "leave_type": leave_type,
        "applied_duration": duration,
        "remaining_balance": getattr(leave_calendar, field_name),
    }


def create_leave_balance(
    db: Session, employee_id: int, leave_type: str, leave_entries: list
):
    # Define mappings for leave types
    leave_fields = {
        "sick": (
            "sick_leave",
            "Sick leave quota is exhausted. You cannot approve the additional sick leave.",
        ),
        "personal": (
            "personal_leave",
            "Personal leave quota is exhausted. You cannot approve the additional personal leave.",
        ),
        "vacation": (
            "vacation_leave",
            "Vacation leave quota is exhausted. You cannot approve the additional vacation leave.",
        ),
        "unpaid": ("unpaid_leave", None),  # No quota check for unpaid leave
    }

    # Retrieve the leave calendar entry for the given employee_id
    leave_calendar = (
        db.query(LeaveCalendar).filter(
            LeaveCalendar.employee_id == employee_id).first()
    )

    if not leave_calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LeaveCalendar entry not found for the specified employee {employee_id}.",
        )

    if leave_type not in leave_fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid leave type specified. Please use 'sick', 'personal', 'vacation', or 'unpaid'.",
        )

    # Get the field name and error message from the mappings
    field_name, error_message = leave_fields[leave_type]

    # Handle unlimited unpaid leave case
    current_balance = getattr(leave_calendar, field_name)

    if leave_type == "unpaid":
        # No decrement or balance check, just return the calendar
        return leave_calendar

    if current_balance is not None and current_balance > 0:
        setattr(leave_calendar, field_name, current_balance - 1)
    else:
        leave_ids = [entry.id for entry in leave_entries if entry is not None]
        data = []
        for d in leave_ids:
            if d is not None:
                data.append(d)
        print(data)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This is the leave ID(s): {data} Please Note This id. This is No More  available {leave_type} leave. You cannot 'apply' {leave_type} Leave. Please select another option from '[sick', 'personal', 'vacation']. ",
        )

    # Commit the changes and handle exceptions
    try:
        db.commit()  # Commit the changes to the database
        # Refresh the instance to reflect updated data
        db.refresh(leave_calendar)
    except Exception as e:
        db.rollback()  # Roll back the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the leave balance.",
        )

    return leave_calendar


def create_employee_leave(
        db: Session, leave: EmployeeLeaveCreate, employee_id: str):
    leave_entries = []
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == employee_id)
        .first()
    )

    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' Not found",
        )

    def map_leave_duration(leave_duration_str: str):
        if leave_duration_str.lower() == "oneday":
            return LeaveDuration.ONE_DAY
        elif leave_duration_str.lower() == "halfday":
            return LeaveDuration.HALF_DAY
        else:
            raise ValueError("Invalid leave duration")

    leave.duration = map_leave_duration(leave.duration.value)
    leave_type = leave.leave_type

    for i in range(leave.total_days):
        end_date = leave.start_date + timedelta(days=i)
        db_leave = EmployeeLeave(
            employee_id=employee_data.id,
            leave_type=leave.leave_type,
            duration=leave.duration,
            start_date=leave.start_date + timedelta(days=i),
            end_date=end_date,
            reason=leave.reason,
        )

        leave_entries.append(db_leave)
        db.add(db_leave)

        # Call create_leave_balance and handle its return
        balance = create_leave_balance(
            db, employee_data.id, leave_type, leave_entries)
        print("Updated leave calendar:", balance)

    db.commit()
    employee_code = employee_data.employee_id
    employee_email = employee_data.employee_email
    employee_firstname = employee_data.employee.firstname
    employee_lastname = employee_data.employee.lastname
    other_leave_ids = [leave.id for leave in leave_entries]

    return {
        "leave": db_leave.id,
        "reason": db_leave.reason,
        "status": db_leave.status.value,
        "employee_email": employee_email,
        "employee_code": employee_code,
        "employee_firstname": employee_firstname,
        "employee_lastname": employee_lastname,
        "other_entries": other_leave_ids,
    }


def get_employee_leave_by_month(
        db: Session, employee_id: str, month: int, year: int):
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == employee_id)
        .first()
    )
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' Not found",
        )
    data = (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.employee_id == employee_data.id,
            func.extract("month", EmployeeLeave.start_date) == month,
            func.extract("year", EmployeeLeave.start_date) == year,
        )
        .all()
    )
    if not data:
        return {"detail": f" No leaves Applied for This Month to '{employee_id}' "}
    structured_data = [
        {
            "Leave ID": leave.id,
            "Employee ID": leave.employee.employee_id,
            "Leave Type": leave.leave_type,
            "Duration": leave.duration,
            "Reason": leave.reason,
            "Start Date": leave.start_date,
            "End Date": leave.end_date,
            "Status": leave.status,
            "Reject Reason": leave.reject_reason,
        }
        for leave in data
    ]
    
    return structured_data


def get_employee_leave_by_month_tl(
    db: Session, employee_id: str, report_manager: str, month: int, year: int
):
    data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.employee_id == employee_id,
            EmployeeEmploymentDetails.reporting_manager == report_manager,
        )
        .first()
    )
    if data:
        return (
            db.query(EmployeeLeave)
            .filter(
                EmployeeLeave.employee_id == data.id,
                func.extract("month", EmployeeLeave.start_date) == month,
                func.extract("year", EmployeeLeave.start_date) == year,
            )
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Employee '{employee_id}' Not found",
    )

def get_leave_for_slip(db: Session, current_employee_id: str,month:int,year:int):
    data_id = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == current_employee_id)
        .first()
    )
    if not data_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Employee id: '{current_employee_id}' not found")

    data= (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.status == "approved", EmployeeLeave.employee_id == data_id.id ,
            EmployeeLeave.leave_type == "unpaid" ,
            extract('month',EmployeeLeave.start_date)==month,
            extract('year',EmployeeLeave.start_date)==year,
        )
        .all()
    )
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No leaves Found for this Employee id: '{current_employee_id}'")
    return data


def get_leave_by_employee_id(db: Session, employee_id: str):
    # Retrieve employee data based on the employee_id
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == employee_id)
        .first()
    )
    
    # Raise an exception if the employee is not found
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )
    
    # Retrieve all leave records for the found employee
    leave_records = (
        db.query(EmployeeLeave)
        .filter(EmployeeLeave.employee_id == employee_data.id)
        .all()
    )
    
    # Structure the leave records for output
    leave_details = [
        {
            "Leave id": leave.id,
            "employee_id": leave.employee.employee_id,
            "leave_type": leave.leave_type,
            "start_date": leave.start_date,
            "duration": leave.duration,  # Assuming you have a 'duration' field in EmployeeLeave
            "status": leave.status,
            "reject_reason": leave.reject_reason,
        }
        for leave in leave_records
    ]
    
    return leave_details

def get_leave_by_employee_team(
        db: Session, employee_id: str, report_manager: str):
    # Query to get employee data based on employee_id and report_manager
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.employee_id == employee_id,
            EmployeeEmploymentDetails.reporting_manager == report_manager,
        )
        .first()
    )
    if employee_data:  # If employee data is found, return their leave records
        leave_records = (
            db.query(EmployeeLeave)
            .filter(EmployeeLeave.employee_id == employee_data.id)
            .all()
        )

        return leave_records

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Can Not Access Employee {employee_id} Details",
    )


def get_leave_by_id(db: Session, current_employee_id: str):
    data_id = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == current_employee_id)
        .first()
    )
    if not data_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee id: '{current_employee_id}' not found",
        )

    return (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.status == "pending", EmployeeLeave.employee_id == data_id.id
        )
        .all()
    )


def get_leave_by_admin(db: Session):
    return db.query(EmployeeLeave).filter(
        EmployeeLeave.status == "pending").all()


def get_leave_by_report_manager(db: Session, report_manager_id: str):
    # Query to get all employees reporting to the given manager
    manager = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == report_manager_id)
        .first()
    )
    employees = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.reporting_manager == report_manager_id)
        .all()
    )
    # If no employees found, raise a 404 error
    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employees found for this reporting manager",
        )

    # Extract the employee IDs from the employment details
    employee_ids = [employee.id for employee in employees]
    # Query to get all pending leave records for the employees
    leave_details = (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.employee_id.in_(employee_ids),
            EmployeeLeave.status == "pending",
        )
        .all()
    )

    # If no leave records found, raise a 404 error
    if not leave_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Pending Leave Records Found for this Team Employees ",
        )

    return leave_details


def update_employee_leave(db: Session, leave_update: EmployeeLeaveUpdate):
    # Query to find the leave request of the employee
    db_leave = (
        db.query(EmployeeLeave)
        .filter(EmployeeLeave.id == leave_update.leave_id)
        .first()
    )
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found for leave id:{leave_update.leave_id}",
        )
    employee_id = db_leave.employee_id
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.id == employee_id,
        )
        .first()
    )
    # If employee not found, raise an exception
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee id:{employee_id} not found",
        )

    # If leave request found, update the details
    if db_leave:
        if leave_update.status == LeaveStatus.APPROVED.value:
            db_leave.status = LeaveStatus.APPROVED
            if leave_update.reason:
                db_leave.reject_reason = leave_update.reason
            else:
                db_leave.reject_reason = f"Leave Granted for Employee id :{employee_id}"
        if leave_update.reason and leave_update.status == LeaveStatus.REJECTED.value:
            db_leave.status = LeaveStatus.REJECTED
            db_leave.reject_reason = leave_update.reason
        leave_type = normalize_string(db_leave.leave_type)
        duration = db_leave.duration.value
        adjust_leave_balance(
            db, employee_id, employee_data.employee_id, leave_type, duration
        )
        db.commit()  # Commit the changes
        db.refresh(db_leave)  # Refresh the instance
    if not db_leave or db_leave.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found for leave id:{db_leave.id}",
        )
        # Set the employee email for sending a notification

        # Send an email notification asynchronously
    # Make sure to return a regular, synchronous object (not a coroutine)
    employee_code = employee_data.employee_id
    employee_email = employee_data.employee_email
    employee_firstname = employee_data.employee.firstname
    employee_lastname = employee_data.employee.lastname
    return {
        "leave": db_leave.id,
        "reason": db_leave.reason,
        "status": db_leave.status.value,
        "employee_email": employee_email,
        "employee_code": employee_code,
        "employee_firstname": employee_firstname,
        "employee_lastname": employee_lastname,
        "other_entires": " ",
    }


def update_employee_teamlead(
    db: Session, report_manager: str, leave_update: EmployeeLeaveUpdate
):
    db_leave = (
        db.query(EmployeeLeave)
        .filter(EmployeeLeave.id == leave_update.leave_id)
        .first()
    )
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found for leave id:{leave_update.leave_id}",
        )
    employee_id = db_leave.employee_id
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.id == employee_id,
            EmployeeEmploymentDetails.reporting_manager == report_manager,
        )
        .first()
    )
    # If employee not found, raise an exception
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee not found or not authenticated to access the employee {employee_id}",
        )

    # If leave request found, update the details
    if db_leave:
        if leave_update.status == LeaveStatus.APPROVED.value:
            db_leave.status = LeaveStatus.APPROVED
            if leave_update.reason:
                db_leave.reject_reason = leave_update.reason
            else:
                db_leave.reject_reason = "Leave Granted"

        if leave_update.reason and leave_update.status == LeaveStatus.REJECTED.value:
            db_leave.status = LeaveStatus.REJECTED
            db_leave.reject_reason = leave_update.reason
        leave_type = normalize_string(db_leave.leave_type)
        duration = db_leave.duration.value
        adjust_leave_balance(
            db, employee_id, employee_data.employee_id, leave_type, duration
        )
        db.commit()  # Commit the changes
        db.refresh(db_leave)  # Refresh the instance
    if not db_leave or db_leave.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found for leave id:{db_leave.id}",
        )
        # Set the employee email for sending a notification

        # Send an email notification asynchronously
    # Make sure to return a regular, synchronous object (not a coroutine)
    employee_code = employee_data.employee_id
    employee_email = employee_data.employee_email
    employee_firstname = employee_data.employee.firstname
    employee_lastname = employee_data.employee.lastname
    return {
        "leave": db_leave.id,
        "reason": db_leave.reason,
        "status": db_leave.status.value,
        "employee_email": employee_email,
        "employee_code": employee_code,
        "employee_firstname": employee_firstname,
        "employee_lastname": employee_lastname,
        "other_entires": " ",
    }


# Delete a leave
def delete_employee_leave(db: Session, employee_id: str, leave_id: int):
    db_leave = (
        db.query(EmployeeLeave)
        .filter(
            EmployeeLeave.employee_id == employee_id,
            EmployeeLeave.id == leave_id,
            EmployeeLeave.status == "pending",
        )
        .first()
    )
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" No pending Leave  in leave id : '{leave_id}' ",
        )
    db.delete(db_leave)
    db.commit()
    return db_leave


def leave_calender(db: Session):
    # Retrieve roles for the given employee_id and role_id
    roles = db.query(employee_role).all()

    for role in roles:
        # Get role data from the Role table
        role_data = db.query(Role).filter(Role.id == role.role_id).first()
        if not role_data:
            continue  # Skip if no role data is found
        # Check if an entry already exists in LeaveCalendar
        leave_calendar = (
            db.query(LeaveCalendar)
            .filter(LeaveCalendar.employee_id == role.employee_id)
            .first()
        )

        if leave_calendar:
            # Update existing LeaveCalendar entry
            leave_calendar.sick_leave = role_data.sick_leave
            leave_calendar.personal_leave = role_data.personal_leave
            leave_calendar.vacation_leave = role_data.vacation_leave
        else:
            # Create a new LeaveCalendar entry
            leave_calendar = LeaveCalendar(
                employee_id=role.employee_id,
                sick_leave=role_data.sick_leave,
                personal_leave=role_data.personal_leave,
                vacation_leave=role_data.vacation_leave,
            )
            db.add(leave_calendar)
            print(leave_calendar)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error saving leave calendar data",
        )

    return {"detail": "Leave calendar created successfully"}


def get_calender(db: Session, employee_id: int):
    data = (
        db.query(LeaveCalendar).filter(
            LeaveCalendar.employee_id == employee_id).first()
    )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave calendar Not Found for the Employee: {employee_id}",
        )
    return {
        "sick_leave": data.sick_leave,
        "personal_leave": data.personal_leave,
        "vacation_leave": data.vacation_leave,
        "Unpaid_leave": data.unpaid_leave
    }


def get_calender_tl(db: Session, report_manager: str, employee_id: str):
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.employee_id == employee_id,
            EmployeeEmploymentDetails.reporting_manager == report_manager,
        )
        .first()
    )
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not Found or not Authenticate to View Details",
        )
    data = (
        db.query(LeaveCalendar)
        .filter(LeaveCalendar.employee_id == employee_data.id)
        .first()
    )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Please ask admin to create leave calender to {employee_id}",
        )

    return {
        "sick_leave": data.sick_leave,
        "personal_leave": data.personal_leave,
        "vacation_leave": data.vacation_leave,
        "Unpaid_leave": data.unpaid_leave
    }
def get_employee_tl(db: Session, report_manager: str):
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(
            EmployeeEmploymentDetails.reporting_manager == report_manager,
        )
        .all()
    )
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{report_manager}' not Found or not Authenticate to View Details",
        )
    return employee_data

def get_calender_admin(db: Session, employee_id: str):
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == employee_id)
        .first()
    )
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee id:{employee_id} is not found",
        )
    data = (
        db.query(LeaveCalendar)
        .filter(LeaveCalendar.employee_id == employee_data.id)
        .first()
    )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave not found in Calender for this Employee id:'{employee_id}'",
        )
    return {
        "sick_leave": data.sick_leave,
        "personal_leave": data.personal_leave,
        "vacation_leave": data.vacation_leave,
        "Unpaid_leave": data.unpaid_leave
    }


def update_leave_calendar(db: Session, leave_update: LeaveCalendarUpdate):
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == leave_update.employee_id)
        .first()
    )
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f" Employee id :'{leave_update.employee_id}' is Not Found",
        )
    leave_calendar = (
        db.query(LeaveCalendar)
        .filter(LeaveCalendar.employee_id == employee_data.id)
        .first()
    )
    if leave_calendar:
        for key, value in leave_update.dict(exclude_unset=True).items():
            if key == "employee_id":
                continue
            setattr(leave_calendar, key, value)
        db.commit()
        db.refresh(leave_calendar)
        return leave_calendar
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LeaveCalendar entry not found for Employee id :{leave_update.employee_id}",
        )
