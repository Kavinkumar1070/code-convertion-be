from datetime import datetime, timedelta
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from src.models.chathistory import ChatHistory
from src.models.employee import EmployeeEmploymentDetails
from sqlalchemy import text
from datetime import datetime
from typing import List
def create_chat_message(db: Session, employee_id: int, question: str, response: str):
    expiration_time = datetime.now() + timedelta(days=5)  # Set to expire in 30 days
    employee=db.query(EmployeeEmploymentDetails).filter(EmployeeEmploymentDetails.employee_id==employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Employee '{employee_id}' is Not Found")
    chat_message = ChatHistory(
        employee_id=employee_id,
        question=question,
        response=response,
        expiration_timestamp=expiration_time
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message

from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List



def get(db: Session, employee_id: int) -> List[dict]:
    employee_history = db.query(ChatHistory).filter(ChatHistory.employee_id == employee_id).all()

    # Check if history is empty
    if not employee_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No History available for '{employee_id}'")

    data = []

    # Iterate over each employee history record
    for emp in employee_history:
        # Check if emp.timestamp is None or not a string
        if isinstance(emp.timestamp, str):
            history_create_dt = datetime.fromisoformat(emp.timestamp)  # Convert from ISO format
        elif isinstance(emp.timestamp, datetime):
            history_create_dt = emp.timestamp  # Already a datetime object
        else:
            raise ValueError(f"Unexpected timestamp type: {type(emp.timestamp)}")

        # Check for expiration timestamp similarly
        if isinstance(emp.expiration_timestamp, str):
            history_expire_dt = datetime.fromisoformat(emp.expiration_timestamp)
        elif isinstance(emp.expiration_timestamp, datetime):
            history_expire_dt = emp.expiration_timestamp
        else:
            raise ValueError(f"Unexpected expiration timestamp type: {type(emp.expiration_timestamp)}")

        # Format the datetime objects into a more user-friendly string
        formatted_create = history_create_dt.strftime("%B %d, %Y, %I:%M %p")
        formatted_expire = history_expire_dt.strftime("%B %d, %Y, %I:%M %p")

        data.append({
            "Question": emp.question,
            "Answer": emp.response,
            "History_create": formatted_create,
            "History_Expire": formatted_expire,
        })

    return data





def delete_expired_messages(db: Session):
    db.execute(
        text("DELETE FROM chat_history WHERE expiration_timestamp < NOW()"),
        
    )
    print("delete")
    db.commit()