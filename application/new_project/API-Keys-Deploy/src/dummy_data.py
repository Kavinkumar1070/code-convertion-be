from datetime import datetime, date
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from models import (
    Base,
    EmployeeOnboarding,
    EmployeeEmploymentDetails,
    Role,
    RoleFunction,
    employee_role,
)
from src.models.leave import EmployeeLeave, LeaveDuration, LeaveStatus
from src.core.utils import hash_password
from fastapi import FastAPI
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# Create a new engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Create metadata
metadata = MetaData()


def insert_dummy_data():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Insert roles
        # Dummy data for roles
    admin_role = Role(
        name="admin",
        sick_leave=10,
        personal_leave=5,
        vacation_leave=15
    )

    teamlead_role = Role(
        name="teamlead",
        sick_leave=8,
        personal_leave=4,
        vacation_leave=12
    )

    employee_role = Role(
        name="employee",
        sick_leave=6,
        personal_leave=3,
        vacation_leave=10
    )


    session.add_all([admin_role, teamlead_role, employee_role])
    session.commit()

    # Insert role functions

    #POST
    admin_functions = [
        RoleFunction(
            role_id=admin_role.id,
            function="create personal detail",
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function="create new role",
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='create role function',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function="create new leave",
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='create leave calender',
            jsonfile="admin.json",
        ),
        #GET
        RoleFunction(
            role_id=admin_role.id,
            function='get team members',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get personal detail',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get employee detail',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get role',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get role function',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get pending leaves',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get leave history',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get leave calender',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='get my activity',
            jsonfile="admin.json",
        ),
        #PUT
        RoleFunction(
            role_id=admin_role.id,
            function='update personal detail',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='update employee detail',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='update role',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='update role function',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='update leave status',
            jsonfile="admin.json",
        ),
        RoleFunction(
            role_id=admin_role.id,
            function='update leave calender',
            jsonfile="admin.json",
        ),RoleFunction(
            role_id=admin_role.id,
            function='update password',
            jsonfile="admin.json",
        ),
        #DELETE
        RoleFunction(
            role_id=admin_role.id,
            function='delete employee detail',
            jsonfile="admin.json",
        ),RoleFunction(
            role_id=admin_role.id,
            function='delete role',
            jsonfile="admin.json",
        ),RoleFunction(
            role_id=admin_role.id,
            function='delete role function',
            jsonfile="admin.json",
        ),RoleFunction(
            role_id=admin_role.id,
            function='delete leave record',
            jsonfile="admin.json",
        )
]

    teamlead_functions = [
        #POST
        RoleFunction(
            role_id=teamlead_role.id,
            function='apply new leave',
            jsonfile="teamlead.json",
        ),
        #GET
        RoleFunction(
            role_id=teamlead_role.id,
            function='Read employee detail',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get team members',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get leave details',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get pending leaves',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get pending leaves of employee',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get leave history',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get leave calender',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get employee leave calender',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='get my activity',
            jsonfile="teamlead_role.json",
        ),
        #PUT
        RoleFunction(
            role_id=teamlead_role.id,
            function='update personal detail',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='update leave status',
            jsonfile="teamlead.json",
        ),
        RoleFunction(
            role_id=teamlead_role.id,
            function='update password',
            jsonfile="teamlead.json",
        ),

        #DELETE
        RoleFunction(
            role_id=teamlead_role.id,
            function='delete leave record',
            jsonfile="teamlead.json",
        )
]

    employee_functions = [
        #POST
        RoleFunction(
            role_id=employee_role.id,
            function='apply new leave',
            jsonfile="employee.json",
        ),
        #GET
        RoleFunction(
            role_id=employee_role.id,
            function='Read employee detail',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='get leave details',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='get pending leaves',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='get leave history',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='get leave calender',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='get my activity',
            jsonfile="employee.json",
        ),
        #PUT
        RoleFunction(
            role_id=employee_role.id,
            function='update personal detail',
            jsonfile="employee.json",
        ),
        RoleFunction(
            role_id=employee_role.id,
            function='update password',
            jsonfile="employee.json",
        ),

        #DELETE
        RoleFunction(
            role_id=employee_role.id,
            function='delete leave record',
            jsonfile="employee.json",
        )
]

    session.add_all(admin_functions + teamlead_functions + employee_functions)
    session.commit()

    # Insert employees
    admin_employee = EmployeeOnboarding(
        employment_id="cds0001",
        firstname="admin",
        lastname="admin",
        dateofbirth=date(1985, 7, 10),
        contactnumber=1112233445,
        emailaddress="hariprathap670@gmail.com",
        address="123 Admin St",
        nationality="American",
        gender="male",
        maritalstatus="Single",
    )

    teamlead_employee = EmployeeOnboarding(
        employment_id="cds0002",
        firstname="teamlead",
        lastname="tl",
        dateofbirth=date(1988, 3, 22),
        contactnumber=5556677889,
        emailaddress="kavin@gmail.com",
        address="456 Leader Rd",
        nationality="American",
        gender="Male",
        maritalstatus="Married",
    )

    regular_employee = EmployeeOnboarding(
        employment_id="cds0003",
        firstname="employee",
        lastname="emp",
        dateofbirth=date(1992, 11, 5),
        contactnumber=9998887770,
        emailaddress="employee@gmail.com",
        address="789 Worker Ave",
        nationality="American",
        gender="Non-Binary",
        maritalstatus="Single",
    )
    
    admin_employee1 = EmployeeOnboarding(
        employment_id="cds0004",
        firstname="kavinkumar",
        lastname="k",
        dateofbirth=date(1995, 9, 18),
        contactnumber=8508750558,
        emailaddress="kavinkumartpm@gmail.com",
        address="Anthiyur,erode",
        nationality="Indian",
        gender="male",
        maritalstatus="Single",
    )

    teamlead_employee1 = EmployeeOnboarding(
        employment_id="cds0005",
        firstname="hariprathap",
        lastname="v",
        dateofbirth=date(2004, 3, 30),
        contactnumber=9025913881,
        emailaddress="hariprathap670@gmail.com",
        address="sathy",
        nationality="indian",
        gender="Male",
        maritalstatus="Married",
    )

    regular_employee1 = EmployeeOnboarding(
        employment_id="cds0006",
        firstname="sidthik",
        lastname="m",
        dateofbirth=date(2001, 3, 18),
        contactnumber=9003843494,
        emailaddress="sidthikabu18@gmail.com",
        address="thanjavur",
        nationality="indian",
        gender="male",
        maritalstatus="married",
    )


    session.add_all([admin_employee, teamlead_employee, regular_employee,admin_employee1, teamlead_employee1, regular_employee1])
    session.commit()

    # Insert employment details
    admin_password = hash_password("adminpass123")
    teamlead_password = hash_password("teamleadpass456")
    employee_password = hash_password("emppass789")
    admin_password1 = hash_password("adminpass123")
    teamlead_password1 = hash_password("teamleadpass456")
    employee_password1 = hash_password("emppass789")


    admin_employment_details = EmployeeEmploymentDetails(
        employee_email="admin@conversedatasolution.com",
        password=admin_password,
        job_position="Administrator",
        department="Administration",
        start_date=date(2020, 1, 1),
        employment_type="Full-time",
        reporting_manager=None,
        work_location="Main Office",
        basic_salary=80000.00,
        employee_id=admin_employee.employment_id,  # Must match admin_employee.employment_id
    )

    teamlead_employment_details = EmployeeEmploymentDetails(
        employee_email="teamlead@conversedatasolution.com",
        password=teamlead_password,
        job_position="Team Leader",
        department="Engineering",
        start_date=date(2021, 6, 1),
        employment_type="Full-time",
        reporting_manager="cds0001",
        work_location="Main Office",
        basic_salary=75000.00,
        employee_id=teamlead_employee.employment_id,  # Must match teamlead_employee.employment_id
    )

    regular_employment_details = EmployeeEmploymentDetails(
        employee_email="employee@conversedatasolution.com",
        password=employee_password,
        job_position="Software Engineer",
        department="Engineering",
        start_date=date(2022, 3, 15),
        employment_type="Full-time",
        reporting_manager="cds0002",
        work_location="Main Office",
        basic_salary=70000.00,
        employee_id=regular_employee.employment_id,  # Must match regular_employee.employment_id
    )
    
    admin_employment_details1 = EmployeeEmploymentDetails(
        employee_email="kavin@conversedatasolutions.com",
        password=admin_password1,
        job_position="Administrator",
        department="Administration",
        start_date=date(2020, 5, 1),
        employment_type="Full-time",
        reporting_manager="cds0001",
        work_location="Main Office",
        basic_salary=100000.00,
        employee_id=admin_employee1.employment_id,  # Must match admin_employee.employment_id
    )

    teamlead_employment_details1 = EmployeeEmploymentDetails(
        employee_email="hariprathap@conversedatasolutions.com",
        password=teamlead_password1,
        job_position="Team Leader",
        department="Engineering",
        start_date=date(2021, 7, 1),
        employment_type="Full-time",
        reporting_manager="cds0004",
        work_location="Main Office",
        basic_salary=95000.00,
        employee_id=teamlead_employee1.employment_id,  # Must match teamlead_employee.employment_id
    )

    regular_employment_details1 = EmployeeEmploymentDetails(
        employee_email="sidthik@conversedatasolutions.com",
        password=employee_password1,
        job_position="Software Engineer",
        department="Engineering",
        start_date=date(2022, 3, 15),
        employment_type="Full-time",
        reporting_manager="cds0005",
        work_location="Main Office",
        basic_salary=40000.00,
        employee_id=regular_employee1.employment_id,  # Must match regular_employee.employment_id
    )

    session.add_all(
        [
            admin_employment_details,
            teamlead_employment_details,
            regular_employment_details,
            admin_employment_details1,
            teamlead_employment_details1,
            regular_employment_details1,
        ]
    )
    session.commit()

    # Insert roles
    employee_role_table = Table("employee_role", metadata, autoload_with=engine)

    session.execute(
        employee_role_table.insert().values(
            [
                {"employee_id": admin_employee.id, "role_id": admin_role.id},
                {"employee_id": teamlead_employee.id, "role_id": teamlead_role.id},
                {"employee_id": regular_employee.id, "role_id": employee_role.id},
                {"employee_id": admin_employee1.id, "role_id": admin_role.id},
                {"employee_id": teamlead_employee1.id, "role_id": teamlead_role.id},
                {"employee_id": regular_employee1.id, "role_id": employee_role.id},
            ]
        )
    )
    session.commit()

#     # Insert leaves
#     leaves = [
#     # Admin Employee Leaves
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 10),
#         end_date=date(2024, 9, 10),
#         status=LeaveStatus.APPROVED,
#         reason="Flu",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 12),
#         end_date=date(2024, 9, 12),
#         status=LeaveStatus.APPROVED,
#         reason="Headache",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 18),
#         end_date=date(2024, 9, 18),
#         status=LeaveStatus.PENDING,
#         reason="Beach Trip",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 25),
#         end_date=date(2024, 9, 25),
#         status=LeaveStatus.REJECTED,
#         reason="Urgent Personal Matter",
#         reject_reason="Insufficient Leave Balance",
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 30),
#         end_date=date(2024, 9, 30),
#         status=LeaveStatus.APPROVED,
#         reason="Family Emergency",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 12),
#         end_date=date(2024, 9, 12),
#         status=LeaveStatus.PENDING,
#         reason="Headache",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 15),
#         end_date=date(2024, 9, 15),
#         status=LeaveStatus.PENDING,
#         reason="Weekend Trip",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 20),
#         end_date=date(2024, 9, 20),
#         status=LeaveStatus.PENDING,
#         reason="Family Matter",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 25),
#         end_date=date(2024, 9, 25),
#         status=LeaveStatus.PENDING,
#         reason="Special Event",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=admin_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 28),
#         end_date=date(2024, 9, 28),
#         status=LeaveStatus.PENDING,
#         reason="Vacation",
#         reject_reason=None,
#     ),

#     # Team Lead Employee Leaves
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 15),
#         end_date=date(2024, 9, 15),
#         status=LeaveStatus.PENDING,
#         reason="Family Event",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 22),
#         end_date=date(2024, 9, 22),
#         status=LeaveStatus.APPROVED,
#         reason="Cold",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 25),
#         end_date=date(2024, 9, 25),
#         status=LeaveStatus.REJECTED,
#         reason="Doctor's Appointment",
#         reject_reason="Insufficient Leave Balance",
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 28),
#         end_date=date(2024, 9, 28),
#         status=LeaveStatus.APPROVED,
#         reason="Wedding",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 30),
#         end_date=date(2024, 9, 30),
#         status=LeaveStatus.PENDING,
#         reason="Special Event",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 11),
#         end_date=date(2024, 9, 11),
#         status=LeaveStatus.PENDING,
#         reason="Migraine",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 20),
#         end_date=date(2024, 9, 20),
#         status=LeaveStatus.PENDING,
#         reason="Travel",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 22),
#         end_date=date(2024, 9, 22),
#         status=LeaveStatus.PENDING,
#         reason="Appointment",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 25),
#         end_date=date(2024, 9, 25),
#         status=LeaveStatus.PENDING,
#         reason="Event",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=teamlead_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 27),
#         end_date=date(2024, 9, 27),
#         status=LeaveStatus.PENDING,
#         reason="Holiday",
#         reject_reason=None,
#     ),

#     # Regular Employee Leaves
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 20),
#         end_date=date(2024, 9, 20),
#         status=LeaveStatus.REJECTED,
#         reason="Urgent Personal Matter",
#         reject_reason="Insufficient Leave Balance",
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 21),
#         end_date=date(2024, 9, 21),
#         status=LeaveStatus.APPROVED,
#         reason="Back Pain",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 23),
#         end_date=date(2024, 9, 23),
#         status=LeaveStatus.PENDING,
#         reason="Traveling",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 26),
#         end_date=date(2024, 9, 26),
#         status=LeaveStatus.REJECTED,
#         reason="Family Matter",
#         reject_reason="Insufficient Leave Balance",
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 29),
#         end_date=date(2024, 9, 29),
#         status=LeaveStatus.APPROVED,
#         reason="Extended Leave",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="sick",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 11),
#         end_date=date(2024, 9, 11),
#         status=LeaveStatus.PENDING,
#         reason="Fever",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 15),
#         end_date=date(2024, 9, 15),
#         status=LeaveStatus.PENDING,
#         reason="Break",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="personal",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 18),
#         end_date=date(2024, 9, 18),
#         status=LeaveStatus.PENDING,
#         reason="Errand",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="unpaid",
#         duration=LeaveDuration.ONE_DAY,
#         start_date=date(2024, 9, 22),
#         end_date=date(2024, 9, 22),
#         status=LeaveStatus.PENDING,
#         reason="Unpaid Leave",
#         reject_reason=None,
#     ),
#     EmployeeLeave(
#         employee_id=regular_employee.id,
#         leave_type="vacation",
#         duration=LeaveDuration.HALF_DAY,
#         start_date=date(2024, 9, 27),
#         end_date=date(2024, 9, 27),
#         status=LeaveStatus.PENDING,
#         reason="Break",
#         reject_reason=None,
#     ),
# ]

#     session.add_all(leaves)
#     session.commit()


if __name__ == "__main__":
    insert_dummy_data()
    print("Dummy data inserted successfully.")
