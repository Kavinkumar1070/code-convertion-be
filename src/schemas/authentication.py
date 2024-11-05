from pydantic import BaseModel


class TokenData(BaseModel):
    employee_id: int | None = None

class ChangePassword(BaseModel):
    current_password:str
    new_password:str
    confirm_password:str

    