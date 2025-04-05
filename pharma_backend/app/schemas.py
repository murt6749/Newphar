from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class StudyPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    goal: str
    duration_weeks: int
    intensity: str
    start_date: datetime
    end_date: datetime

class StudyPlanCreate(StudyPlanBase):
    pass

class StudyPlan(StudyPlanBase):
    id: int
    owner_id: int
    is_active: bool

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    duration_hours: float
    priority: str
    study_plan_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int
    is_completed: bool

    class Config:
        from_attributes = True

class AIPlanRequest(BaseModel):
    materials: Optional[str] = None
    topics: List[str]
    duration_weeks: int
    intensity: str
    goal: str

class AIChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class FileUpload(BaseModel):
    filename: str
    content_type: str
    content: bytes