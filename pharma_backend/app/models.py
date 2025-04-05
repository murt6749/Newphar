from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    
    study_plans = relationship("StudyPlan", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    goal = Column(String)
    duration_weeks = Column(Integer)
    intensity = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="study_plans")
    tasks = relationship("Task", back_populates="study_plan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(DateTime)
    duration_hours = Column(Integer)
    priority = Column(String)
    is_completed = Column(Boolean, default=False)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    study_plan = relationship("StudyPlan", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")