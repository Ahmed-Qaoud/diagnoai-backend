from datetime import datetime, UTC
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from app.models.user import User

class AnalysisBase(SQLModel):
    analysis_type: str = "CBC"
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    result_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

class Analysis(AnalysisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    user: User = Relationship(back_populates="analyses")

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisRead(AnalysisBase):
    id: int
    user_id: int
    created_at: datetime
