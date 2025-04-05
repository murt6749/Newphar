from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email,
        hashed_password=fake_hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_study_plans(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.StudyPlan).filter(
        models.StudyPlan.owner_id == user_id
    ).offset(skip).limit(limit).all()

def create_user_study_plan(db: Session, study_plan: schemas.StudyPlanCreate, user_id: int):
    db_study_plan = models.StudyPlan(**study_plan.dict(), owner_id=user_id)
    db.add(db_study_plan)
    db.commit()
    db.refresh(db_study_plan)
    return db_study_plan

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(
        models.Task.owner_id == user_id
    ).offset(skip).limit(limit).all()

def create_user_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_date(db: Session, user_id: int, date: datetime):
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = datetime.combine(date, datetime.max.time())
    return db.query(models.Task).filter(
        models.Task.owner_id == user_id,
        models.Task.due_date >= start_of_day,
        models.Task.due_date <= end_of_day
    ).all()

def complete_task(db: Session, task_id: int, user_id: int):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()
    if db_task:
        db_task.is_completed = True
        db.commit()
        db.refresh(db_task)
    return db_task