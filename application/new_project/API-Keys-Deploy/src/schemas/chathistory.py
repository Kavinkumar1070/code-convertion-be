from pydantic import BaseModel



class ChatHistoryCreate(BaseModel):
    question: str
    response: str