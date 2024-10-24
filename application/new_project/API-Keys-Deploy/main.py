from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from starlette.responses import RedirectResponse
from src.core.database import engine, SessionLocal
from src import models
from src.routers import personal, employee, role, leave, admin, general,chathistory
from src.core.authentication import router as auth_router, oauth2_scheme, get_current_user_function
from src.crud.chathistory import delete_expired_messages
import logging
from src.core.database import get_db

app = FastAPI()

# Create all database tables
models.Base.metadata.create_all(bind=engine)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000","http://127.0.0.1:5000","http://localhost:5000", "https://employee-chat-fe-dev-43e1f5279cb7.herokuapp.com","https://employee-chat-fe-model-dev-221d3977ca1e.herokuapp.com"],  # Allow Live Server URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(personal.router)
app.include_router(employee.router)
app.include_router(role.router)
app.include_router(leave.router)
app.include_router(admin.router)
app.include_router(general.router)
app.include_router(chathistory.router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Home route
@app.get("/")
def home():
    return RedirectResponse(url="/docs")

# Profile route
@app.get("/profile/")
async def get_profile(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    print("1345543")
    print(token)
    db_user = get_current_user_function(db, token)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authenticated"
        )
    return db_user

# Update yearly leave balances function
def update_yearly_leave_balances(db: Session):
    employees = db.query(models.EmployeeOnboarding).all()
    for employee in employees:
        employment_details = (
            db.query(models.EmployeeEmploymentDetails)
            .filter(models.EmployeeEmploymentDetails.employee_id == employee.employment_id)
            .first()
        )
        if not employment_details or not employment_details.role_id:
            continue

        role = db.query(models.Role).filter(models.Role.id == employment_details.role_id).first()
        if not role:
            continue

        leave_calendar = db.query(models.LeaveCalendar).filter(models.LeaveCalendar.employee_id == employee.employment_id).first()
        if not leave_calendar:
            continue

        leave_calendar.sick_leave = role.sick_leave
        leave_calendar.personal_leave = role.personal_leave
        leave_calendar.vacation_leave = role.vacation_leave
        leave_calendar.unpaid_leave = 0

        try:
            db.commit()
            db.refresh(leave_calendar)
        except Exception as e:
            db.rollback()
            logging.error(f"Error updating leave for employee {employee.employment_id}: {str(e)}")

# Scheduler to run the task every year
def start_scheduler():
    scheduler = BackgroundScheduler()

    # Job 1: Update yearly leave balances (runs every year on Jan 1st)
    scheduler.add_job(
        update_yearly_leave_balances,
        trigger="cron",
        year="*",
        month="1",
        day="1",
        args=[SessionLocal()],
    )

    # Job 2: Delete expired chat messages (runs every day)
    scheduler.add_job(
        delete_expired_messages,  # Job function for deleting expired messages
        trigger="interval",  # Use 'interval' for recurring jobs
         hours=6,  # Runs every day
        args=[SessionLocal()]  # Pass the database session
    )

    # Start the scheduler
    scheduler.start()

# FastAPI startup event
@app.on_event("startup")
async def on_startup():
    start_scheduler()
