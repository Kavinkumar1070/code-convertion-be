from typing import List

from fastapi import HTTPException, status
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.utils import normalize_string
from src.models.association import employee_role
from src.models.personal import EmployeeOnboarding
from src.models.role import Role, RoleFunction
from src.schemas.role import (EmployeeRole, RoleCreate, RoleFunctionCreate,
                              UpateRoleFunction, UpdateRole)


def create(db: Session, role: RoleCreate):
    role_exists = db.query(Role).filter(Role.name == role.name).first()
    if role_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The Role '{role.name}' is Already exists",
        )
    db_role = Role(
        name=role.name,
        sick_leave=role.sick_leave,
        personal_leave=role.personal_leave,
        vacation_leave=role.vacation_leave,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role(db: Session, role_name: str):
    role = db.query(Role).filter(Role.name == role_name).first()
    return role


def delete(db: Session, db_role: int):
    role = db.query(Role).filter(Role.id == db_role).first()
    db.delete(role)
    db.commit()
    return {"detail": f"Role {db_role} deleted successfully"}


def update(db: Session, update_data: UpdateRole):
    role = db.query(Role).filter(Role.id == update_data.role_id).first()
    try:
        if role:
            # Loop through the update_data dict and update fields dynamically
            for key, value in update_data.dict(exclude_unset=True).items():
                if key == "new_name":
                    setattr(role, "name", normalize_string(value))
                else:
                    setattr(role, key, value)

            db.commit()
            db.refresh(role)
        return role
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{update_data.new_name}' name already exists",
        )


def get(db: Session):
    try:
        # Query all roles from the database
        roles_data = db.query(Role).all()
        
        # Prepare the response data structure
        roles_response = [
            {
                "id": role.id,
                "name": role.name,
                "sick_leave": role.sick_leave,
                "personal_leave": role.personal_leave,
                "vacation_leave": role.vacation_leave,
            }
            for role in roles_data
        ]
        
        return roles_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching roles: {str(e)}"
        )

def get_single(db: Session, role_id: int):
    single_role = db.query(Role).filter(Role.id == role_id).first()
    return single_role


def get_function(db: Session, function: int):
    single_function = db.query(RoleFunction).filter(
        RoleFunction.id == function).first()
    return single_function


def assign_employee_role(db: Session, data: EmployeeRole):
    # Check if the employee exists
    employee_details = (
        db.query(EmployeeOnboarding)
        .filter(EmployeeOnboarding.employment_id == data.employee_id)
        .first()
    )
    if not employee_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee ID:'{data.employee_id}' is not Found",
        )

    # Check if the role exists
    role_details = db.query(Role).filter(Role.id == data.role_id).first()
    if not role_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role ID:'{data.role_id}' is not Found",
        )

    # Check if the employee already has the "Team Leader" role
    existing_role = (
        db.query(employee_role)
        .filter(
            employee_role.c.employee_id == employee_details.id,
            employee_role.c.role_id == data.role_id,
        )
        .first()
    )

    if existing_role:
        return {"detail": f"Employee already has the role '{role_details.name}'"}

    # Check if the employee has the default "Employee" role
    default_role = (
        db.query(employee_role)
        .filter(employee_role.c.employee_id == employee_details.id)
        .first()
    )

    if not default_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee does not have a default role",
        )

    # Update the employee's role from "Employee" to "Team Leader"
    update_statement = (
        employee_role.update()
        .where(employee_role.c.employee_id == employee_details.id)
        .values(role_id=data.role_id)
    )

    db.execute(update_statement)
    db.commit()

    return {"detail": f"Role updated successfully ' {role_details.name}'"}


# RoleFunction CRUD operations
def create_role_function(db: Session, role_function: RoleFunctionCreate):
    role = db.query(Role).filter(Role.id == role_function.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role Id:'{role_function.role_id}' not found",
        )
    db_role_function = RoleFunction(
        role_id=role_function.role_id,
        function=role_function.function,
        jsonfile=role_function.jsonfile,
    )
    db.add(db_role_function)
    db.commit()
    db.refresh(db_role_function)
    return db_role_function


def get_role_functions(db: Session, role_id: int):
    response = db.query(RoleFunction).filter(
        RoleFunction.role_id == role_id).all()
    # Reorganize the result in the desired order and return it
    formatted_result = [
        {
            "id": item.id,
            "role_id": item.role_id,  # Renamed to match requested 'roleid'
            "function": item.function,
        }
        for item in response
    ]
    return formatted_result


def delete_role_function(db: Session, role_function_id: int):
    db_role_function = (
        db.query(RoleFunction).filter(
            RoleFunction.id == role_function_id).first()
    )
    if db_role_function:
        db.delete(db_role_function)
        db.commit()
    return db_role_function


def update_function(db: Session, update_data: UpateRoleFunction):
    function = (
        db.query(RoleFunction)
        .filter(RoleFunction.id == update_data.function_id)
        .first()
    )
    try:
        if function:
            # Loop through the update_data dict and update fields dynamically
            for key, value in update_data.dict(exclude_unset=True).items():
                if key == "function":
                    setattr(function, "function", normalize_string(value))
                if key == "jsonfile":
                    setattr(function, "jsonfile", normalize_string(value))
                else:
                    setattr(function, key, value)

            db.commit()
            db.refresh(function)
        return function
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function '{update_data.function}'already exists",
        )
