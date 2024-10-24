from sqlalchemy import Column,Integer,String,Text,TIMESTAMP,ForeignKey
from src.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates

class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(100), ForeignKey("employee_employment_details.employee_id"))  # Change to String(100)
    question = Column(String(255))
    response = Column(Text)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    expiration_timestamp = Column(TIMESTAMP)

    employee = relationship("EmployeeEmploymentDetails", back_populates='chathistory')
