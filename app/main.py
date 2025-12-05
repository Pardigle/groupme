import json
import uvicorn
import secrets
import string
import os
from pathlib import Path
from typing import Optional, List, Set
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

# GLOBAL CONSTANTS
ALLPOSSIBLETIMES = [
    "0-0800-0830", "0-0830-0900", "0-0900-0930", "0-0930-1000", "0-1000-1030",
    "0-1030-1100", "0-1100-1130", "0-1130-1200", "0-1200-1230", 
    "0-1230-1300", "0-1300-1330", "0-1330-1400", "0-1400-1430", "0-1430-1500",
    "0-1500-1530", "0-1530-1600", "0-1600-1630", "0-1630-1700", "0-1700-1730",
    "0-1730-1800", "0-1800-1830", "0-1830-1900", "0-1900-1930", "0-1930-2000", "", 
    "1-0800-0830", "1-0830-0900", "1-0900-0930", "1-0930-1000", "1-1000-1030",
    "1-1030-1100", "1-1100-1130", "1-1130-1200", "1-1200-1230", 
    "1-1230-1300", "1-1300-1330", "1-1330-1400", "1-1400-1430", "1-1430-1500",
    "1-1500-1530", "1-1530-1600", "1-1600-1630", "1-1630-1700", "1-1700-1730",
    "1-1730-1800", "1-1800-1830", "1-1830-1900", "1-1900-1930", "1-1930-2000", "", 
    "2-0800-0830", "2-0830-0900", "2-0900-0930", "2-0930-1000", "2-1000-1030",
    "2-1030-1100", "2-1100-1130", "2-1130-1200", "2-1200-1230", 
    "2-1230-1300", "2-1300-1330", "2-1330-1400", "2-1400-1430", "2-1430-1500",
    "2-1500-1530", "2-1530-1600", "2-1600-1630", "2-1630-1700", "2-1700-1730",
    "2-1730-1800", "2-1800-1830", "2-1830-1900", "2-1900-1930", "2-1930-2000", "", 
    "3-0800-0830", "3-0830-0900", "3-0900-0930", "3-0930-1000", "3-1000-1030",
    "3-1030-1100", "3-1100-1130", "3-1130-1200", "3-1200-1230", 
    "3-1230-1300", "3-1300-1330", "3-1330-1400", "3-1400-1430", "3-1430-1500",
    "3-1500-1530", "3-1530-1600", "3-1600-1630", "3-1630-1700", "3-1700-1730",
    "3-1730-1800", "3-1800-1830", "3-1830-1900", "3-1900-1930", "3-1930-2000", "", 
    "4-0800-0830", "4-0830-0900", "4-0900-0930", "4-0930-1000", "4-1000-1030",
    "4-1030-1100", "4-1100-1130", "4-1130-1200", "4-1200-1230", 
    "4-1230-1300", "4-1300-1330", "4-1330-1400", "4-1400-1430", "4-1430-1500",
    "4-1500-1530", "4-1530-1600", "4-1600-1630", "4-1630-1700", "4-1700-1730",
    "4-1730-1800", "4-1800-1830", "4-1830-1900", "4-1900-1930", "4-1930-2000", "", 
    "5-0800-0830", "5-0830-0900", "5-0900-0930", "5-0930-1000", "5-1000-1030",
    "5-1030-1100", "5-1100-1130", "5-1130-1200", "5-1200-1230", 
    "5-1230-1300", "5-1300-1330", "5-1330-1400", "5-1400-1430", "5-1430-1500",
    "5-1500-1530", "5-1530-1600", "5-1600-1630", "5-1630-1700", "5-1700-1730",
    "5-1730-1800", "5-1800-1830", "5-1830-1900", "5-1900-1930", "5-1930-2000", "", 
    "6-0800-0830", "6-0830-0900", "6-0900-0930", "6-0930-1000", "6-1000-1030",
    "6-1030-1100", "6-1100-1130", "6-1130-1200", "6-1200-1230", 
    "6-1230-1300", "6-1300-1330", "6-1330-1400", "6-1400-1430", "6-1430-1500",
    "6-1500-1530", "6-1530-1600", "6-1600-1630", "6-1630-1700", "6-1700-1730",
    "6-1730-1800", "6-1800-1830", "6-1830-1900", "6-1900-1930", "6-1930-2000", "", 
]
ALLOWED_TYPES = string.ascii_uppercase + string.digits
PASSCODE_LENGTH = 6

# PYDANTIC MODELS

class Student(BaseModel):
    """
    Represents a student joined in a section
    """
    displayName : str
    contactDetails : str
    schedule : Set[str] = Field(default_factory=set)

class Section(BaseModel):
    """
    Represents a section in the database
    """
    uuid: str
    sectionName : str
    sectionDetails : str = ""
    maxSize : int
    studentList : List[Student] = Field(default_factory=list)

class ScheduleUpdate(BaseModel):
    """
    Represents a data packet for updating a student's schedule.
    
    schedule: Set of string schedules for update.
    """
    schedule: Set[str]

class CreateSection(BaseModel):
    """Payload for creating a section (client-friendly)."""
    sectionName: str
    sectionDetails: str = ""
    maxSize: int

# FASTAPI SETUP

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR/"templates"/"logo"

# DATABASE SETUP

# Replace static DATABASE_PATH / DATABASE_URL logic with environment-aware logic
def _get_database_url(base_dir: Path) -> str:
    """Return a sqlite URL. Prefer GROUPME_DB_PATH, then /tmp, then project dir, then in-memory."""
    env_path = os.environ.get("GROUPME_DB_PATH")
    if env_path:
        p = Path(env_path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{p}"
        except Exception:
            return "sqlite:///:memory:"
    tmp = Path("/tmp")
    if tmp.exists() and os.access(tmp, os.W_OK):
        p = tmp / "groupme.sqlite"
        return f"sqlite:///{p}"
    try:
        p = base_dir / "groupme.sqlite"
        p.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{p}"
    except Exception:
        return "sqlite:///:memory:"

DATABASE_URL = _get_database_url(BASE_DIR)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class SectionORM(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(32), unique=True, index=True, nullable=False)
    sectionName = Column(String, nullable=False)
    sectionDetails = Column(Text, default="")
    maxSize = Column(Integer, nullable=False)
    students = relationship("StudentORM", back_populates="section", cascade="all, delete-orphan", order_by="StudentORM.id")

class StudentORM(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    displayName = Column(String, nullable=False)
    contactDetails = Column(String, nullable=False)
    schedule_json = Column(Text, default="[]")
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    section = relationship("SectionORM", back_populates="students")

    @property
    def schedule(self):
        try:
            return set(json.loads(self.schedule_json))
        except Exception:
            return set()

    @schedule.setter
    def schedule(self, value):
        if value is None:
            value = []
        if isinstance(value, set):
            value = list(value)
        self.schedule_json = json.dumps(list(value))

# Create DB tables but don't crash on import in restricted envs
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # Best effort: if table creation fails (read-only FS), continue using in-memory or existing DB
    # Do not raise so Vercel can import the app; runtime errors will surface on write attempts.
    pass

# Mount static directory only if it exists (Vercel may serve static assets differently)
try:
    if STATIC_DIR.exists():
        app.mount("/logo-assets", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception:
    # skip mounting if it fails in the environment
    pass

# TEMPLATE SETUP

templates = Jinja2Templates(directory=str(BASE_DIR/"templates"))

# ...existing code...