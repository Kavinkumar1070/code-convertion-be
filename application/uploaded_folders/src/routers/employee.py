from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.core.authentication import (get_current_employee,
                                     get_current_employee_roles,
                                     roles_required)
from src.core.database import get_db
from src.core.utils import normalize_string
from src.crud.employee import (create_employee_employment_details,
                               delete_employee_employment_details,
                               get_all_employee_employment_details,
                               get_all_employee_teamlead,
                               get_all_employee_details_slip,
                               update_employee_employment_details)
from src.schemas.employee import (EmployeeEmploymentDetailsCreate,
                                  EmployeeEmploymentDetailsUpdate)

from datetime import datetime
import calendar
import io
import fillpdf.fillpdfs as fillpdfs
from dateutil.relativedelta import relativedelta
from src.core.utils import send_email_with_pdf_attachment
from src.crud.leave import get_leave_for_slip

router = APIRouter(
    prefix="/employee", tags=["employee"], responses={400: {"detail": "Not found"}}
)


@router.get(
    "/employees/reademployee",
    dependencies=[Depends(roles_required("employee", "teamlead"))],
)
async def read_employee(
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    current_employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)

    if employee_role.name == "employee":
        db_employee = get_all_employee_employment_details(
            db, current_employee_id)
    elif employee_role.name == "teamlead":
        db_employee = get_all_employee_employment_details(
            db, current_employee_id)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{current_employee_id}' not found",
        )
    return db_employee

def write_fillable_pdf(input_pdf_path: str, output_pdf_stream: io.BytesIO, data_dict: dict):
    # Fill the PDF with the provided data
    fillpdfs.write_fillable_pdf(input_pdf_path, output_pdf_stream, data_dict)
    
@router.get("/salary-slip/{month}",dependencies=[Depends(roles_required("admin","employee", "teamlead"))])
async def get_salary_slip(month:int,current_employee=Depends(get_current_employee), db: Session = Depends(get_db)):
    try:
        employee_id=current_employee.employment_id
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        new_date = current_date - relativedelta(months=1)
        new_month = new_date.month
        new_year = new_date.year
        db_employee = get_all_employee_details_slip(db, employee_id)
        days_in_month = calendar.monthrange(current_year, month)[1]
        leave = get_leave_for_slip(db, employee_id, month=month, year=new_year)
        leave_data = [leaves.id for leaves in leave]
        count_of_leave = len(leave_data)
        total_days = days_in_month - count_of_leave
        per_day = db_employee.basic_salary / days_in_month
        total_salary = per_day * total_days
        rounded_salary = round(total_salary)

        form_fil = list(fillpdfs.get_form_fields('salary_slip.pdf').keys())
        date_emplo = db_employee.start_date
        # Format the date to only display the date part (without time)
        pay_period = current_date.strftime('%d-%m-%Y')  # You can adjust the format as needed
        date_emplo = date_emplo.strftime('%d-%m-%Y')
        data = {        
            form_fil[0]:date_emplo,  # Date of Joining
            form_fil[1]: pay_period,  # Pay period (only date)
            form_fil[2]: total_days,  # Worked days
            form_fil[3]: db_employee.employee.firstname,  # Employee name
            form_fil[4]: db_employee.job_position,  # Designation
            form_fil[5]: db_employee.department,  # Department
            form_fil[6]: days_in_month,  # Totalwokin days
            form_fil[7]: "0",  # carryover
            form_fil[8]: round(count_of_leave),  # leave days
            form_fil[9]: "0",  # application leave
            form_fil[10]: round(db_employee.basic_salary),  # Fixed pay
            form_fil[11]: "0",  # Days Allownces
            form_fil[12]: round(per_day * count_of_leave),  # Other deductions
            form_fil[13]: "0",  # loan deducction
            form_fil[14]: "0",  # adbsence deductions
            form_fil[15]: round(db_employee.basic_salary),  # Total earings
            form_fil[16]: round(per_day * count_of_leave),  # Total deductions
            form_fil[17]: rounded_salary,  # netpay
        }
   
        #fillpdfs.write_fillable_pdf(input_pdf_path='salary_slip.pdf',output_pdf_path='new.pdf',data_dict=data)
        #Create an in-memory PDF
        pdf_stream = io.BytesIO()
        write_fillable_pdf(input_pdf_path='salary_slip.pdf', output_pdf_stream=pdf_stream, data_dict=data)

        # Move to the beginning of the BytesIO stream
        pdf_stream.seek(0)

        # Send the email with the PDF attachment
        send_email_with_pdf_attachment(db_employee.employee_email, pdf_stream)

        #Close the BytesIO stream
        pdf_stream.close()  # Clear the BytesIO stream from memory

        return {'details':"Salary Slip send to Email Successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    