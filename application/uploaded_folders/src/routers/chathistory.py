from fastapi import APIRouter, HTTPException, status,Depends
from src.core.database import get_db
from src.core.authentication import get_current_employee,roles_required
from src.crud.chathistory import create_chat_message,get
from src.schemas.chathistory import ChatHistoryCreate
from sqlalchemy.orm import Session

router=APIRouter()

@router.post("/create/history",dependencies=[Depends(roles_required("admin","employee", "teamlead"))])
async def create_history(data:ChatHistoryCreate,db:Session=Depends(get_db),current_employee=Depends(get_current_employee)):
    employee_id=current_employee.employment_id
    data= create_chat_message(db,employee_id,data.question,data.response)
    if not  data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="there is Error in Store History")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="History Created Successfully")

@router.get('/history',dependencies=[Depends(roles_required("admin","employee", "teamlead"))])
async def get_history(db:Session=Depends(get_db),current_employee=Depends(get_current_employee)):
    employee_id=current_employee.employment_id
    return get(db,employee_id)