from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List, Optional
import json

from . import models, schemas, crud, auth, ai
from .database import SessionLocal, engine
from .config import settings
from .schemas import UserCreate, Token, User, StudyPlan, StudyPlanCreate, Task, TaskCreate, AIPlanRequest, AIChatRequest

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
origins = [
    "https://murt6749.github.io",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = ai.AIService()

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(auth.get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: User = Depends(auth.get_current_active_user)
):
    return current_user

# Study Plan endpoints
@app.post("/study-plans/", response_model=StudyPlan)
def create_study_plan(
    study_plan: StudyPlanCreate,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    return crud.create_user_study_plan(db=db, study_plan=study_plan, user_id=current_user.id)

@app.get("/study-plans/", response_model=List[StudyPlan])
def read_study_plans(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    return crud.get_study_plans(db, user_id=current_user.id, skip=skip, limit=limit)

# Task endpoints
@app.post("/tasks/", response_model=Task)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    return crud.create_user_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    return crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/tasks/today", response_model=List[Task])
def read_today_tasks(
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    today = datetime.now()
    return crud.get_tasks_by_date(db, user_id=current_user.id, date=today)

@app.post("/tasks/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    return crud.complete_task(db, task_id=task_id, user_id=current_user.id)

# AI endpoints
@app.post("/ai/generate-plan")
async def generate_ai_plan(
    plan_request: AIPlanRequest,
    current_user: User = Depends(auth.get_current_active_user)
):
    try:
        plan = ai_service.generate_study_plan(plan_request)
        return json.loads(plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/chat")
async def ai_chat(
    chat_request: AIChatRequest,
    current_user: User = Depends(auth.get_current_active_user)
):
    try:
        response = ai_service.chat_assistant(chat_request)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze-materials")
async def analyze_materials(
    file: UploadFile = File(...),
    current_user: User = Depends(auth.get_current_active_user)
):
    try:
        # In a real app, you would process the file (PDF, DOCX, etc.)
        # For demo, we'll just read text files
        if file.content_type != "text/plain":
            raise HTTPException(status_code=400, detail="Only text files supported in demo")
        
        text = (await file.read()).decode("utf-8")
        analysis = ai_service.analyze_study_materials(text)
        return json.loads(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoint
@app.get("/stats")
async def get_user_stats(
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(auth.get_db)
):
    tasks = crud.get_tasks(db, user_id=current_user.id)
    completed = sum(1 for t in tasks if t.is_completed)
    pending = len(tasks) - completed
    hours = sum(t.duration_hours for t in tasks if t.is_completed)
    
    # This would be calculated properly in a real app
    streak = 7  # Demo value
    
    return {
        "completed_tasks": completed,
        "pending_tasks": pending,
        "study_hours": hours,
        "streak_days": streak
    }