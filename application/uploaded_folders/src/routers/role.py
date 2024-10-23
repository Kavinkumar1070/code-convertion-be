from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.authentication import (get_current_employee,
                                     get_current_employee_roles,
                                     roles_required)
from src.core.database import get_db
from src.core.utils import normalize_string
from src.crud.role import *
from src.schemas.role import (EmployeeRole, RoleCreate, RoleFunctionCreate,
                              UpateRoleFunction, UpdateRole)

router = APIRouter(
    prefix="/admin/roles", tags=["admin/role"], responses={400: {"detail": "Not found"}}
)


@router.post("", dependencies=[Depends(roles_required("admin"))])
async def create_role(name: RoleCreate, db: Session = Depends(get_db)):
    name.name = normalize_string(name.name)
    if create(db, name):
        return f"'{name.name}' Role and its leaves are Created Successfully"
    return {"detail": f"'{name}' Role is Already Exists"}


@router.delete("/{role_id}", dependencies=[Depends(roles_required("admin"))])
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_single(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role id: '{role_id}' is not found",
        )
    return delete(db, role.id)


@router.put("/", dependencies=[Depends(roles_required("admin"))])
async def update_role(request: UpdateRole, db: Session = Depends(get_db)):
    exists_role = get_single(db, request.role_id)
    if exists_role:
        update(db, request)
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Role id :'{request.role_id}' updated Successfully",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role id: '{request.role_id}' is not found",
        )


@router.get("/", dependencies=[Depends(roles_required("admin"))])
async def get_roles(db: Session = Depends(get_db)):
    role = get(db)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Roles Created, please create new Roles",
        )
    return role


@router.post("/employee/role", dependencies=[Depends(roles_required("admin"))])
def assign_role_to_employee(data: EmployeeRole, db: Session = Depends(get_db)):
    data = assign_employee_role(db, data)
    if data:
        return data


# RoleFunction endpoints
@router.post("/functions/", dependencies=[Depends(roles_required("admin"))])
def create_new_role_function(
    role_function: RoleFunctionCreate, db: Session = Depends(get_db)
):
    return create_role_function(db, role_function)


@router.get("/{role_id}/functions/",
            dependencies=[Depends(roles_required("admin"))])
def read_role_functions(
    role_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
):
    employee_id = current_employee.employment_id
    employee_role = get_current_employee_roles(current_employee.id, db)
    if employee_role.name == "admin":
        data = get_role_functions(db, role_id)
        print("*******************")
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Data Available For This Role Id: {role_id}",
            )
        return data


@router.put("/function/", dependencies=[Depends(roles_required("admin"))])
async def update_functions(request: UpateRoleFunction,
                           db: Session = Depends(get_db)):
    exists_role = get_function(db, request.function_id)
    if exists_role:
        update_function(db, request)
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Function '{request.function}' updated Successfully",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Function id: '{request.function_id}' is not found",
        )


@router.delete("/functions/{id}",
               dependencies=[Depends(roles_required("admin"))])
def delete_existing_role_function(id: int, db: Session = Depends(get_db)):
    db_role_function = delete_role_function(db, id)
    if db_role_function is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role Function for id:'{id}' is not found",
        )
    return db_role_function
