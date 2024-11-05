from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel

router = APIRouter(
    prefix="/general", tags=["general"], responses={400: {"message": "Not found"}}
)

class GeneralQuestion(BaseModel):
    question: str

@router.get("/gen/{user_input}")
def bot_response(user_input:str):
    print('____________')
    print(user_input)
    # Simple bot responses based on keywords
    if 'hello' in user_input.lower():
        return "Hello! How can I assist you today?"
    elif 'how are you' in user_input.lower():
        return "I'm just a bunch of code, but I'm doing great! How about you?"
    elif 'bye' in user_input.lower():
        return "Goodbye! Have a nice day!"
    else:
        return "Sorry, I didn't understand that. Could you please rephrase?"


