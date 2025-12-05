import json
import os
import secrets
import string
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

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "templates" / "logo"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static directory only if it exists
try:
    if STATIC_DIR.exists():
        app.mount("/logo-assets", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception:
    pass

# Initialize templates only if directory exists
try:
    if TEMPLATES_DIR.exists():
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    else:
        templates = None
except Exception:
    templates = None

# DATABASE SETUP (Render)

def _get_database_url(base_dir: Path) -> str:
    """
    Return a sqlite URL for Render deployment.
    Prefer /var/data (Render persistent disk), fall back to project dir.
    """
    # Check for explicit env override
    env_path = os.environ.get("GROUPME_DB_PATH")
    if env_path:
        p = Path(env_path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{p}"
        except Exception:
            pass
    
    # Render: use /var/data for persistent storage (persistent disk mount)
    data_dir = Path("/var/data")
    if data_dir.exists() and os.access(data_dir, os.W_OK):
        p = data_dir / "groupme.sqlite"
        return f"sqlite:///{p}"
    
    # Fallback: use project directory
    try:
        db_dir = base_dir / ".data"
        db_dir.mkdir(parents=True, exist_ok=True)
        p = db_dir / "groupme.sqlite"
        return f"sqlite:///{p}"
    except Exception:
        pass
    
    # Last resort: in-memory (data lost on restart)
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

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

# HELPER FUNCTIONS

def create_passcode():
    chars = [secrets.choice(ALLOWED_TYPES) 
             for i in range(PASSCODE_LENGTH)]
    return ''.join(chars)

def orm_student_to_pydantic(sorm: StudentORM) -> Student:
    return Student(displayName=sorm.displayName,
                   contactDetails=sorm.contactDetails,
                   schedule=set(sorm.schedule))

def orm_section_to_pydantic(sorm: SectionORM, db_session: Session) -> Section:
    students = db_session.query(StudentORM).filter_by(section_id=sorm.id).order_by(StudentORM.id).all()
    p_students = [orm_student_to_pydantic(s) for s in students]
    return Section(uuid=sorm.uuid, sectionName=sorm.sectionName,
                   sectionDetails=sorm.sectionDetails, maxSize=sorm.maxSize,
                   studentList=p_students)

def get_section_orm(passcode: str, db_session: Session) -> Optional[SectionORM]:
    return db_session.query(SectionORM).filter_by(uuid=passcode).first()

def get_students_for_section(sorm: SectionORM, db_session: Session) -> List[StudentORM]:
    return db_session.query(StudentORM).filter_by(section_id=sorm.id).order_by(StudentORM.id).all()

def validate_student_in_section(section: Section, student_id: int) -> bool:
    return 0 <= student_id < len(section.studentList)

def validate_student_and_get_section(passcode: str, student_id: int) -> Optional[Section]:
    with SessionLocal() as session:
        sorm = get_section_orm(passcode, session)
        if sorm is None:
            return None
        p_section = orm_section_to_pydantic(sorm, session)
        if validate_student_in_section(p_section, student_id):
            return p_section
    return None

def similar_hours_cumulative(currentStudent: Student, currentSection: Section):
    similarHours = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    student_id = 0
    for student in rankingList:
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append((student.displayName, len(similarSched) * 0.5,
                                 student.contactDetails, student_id))
        student_id += 1
    return similarHours

def similar_hours_consecutive(currentStudent: Student, currentSection: Section):
    allStudentsChunks = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    student_id = 0
    for student in rankingList:
        if student != currentStudent:
            comparedSched = student.schedule
            currentLength = 0
            maxLength = 0
            for slot in ALLPOSSIBLETIMES:
                if slot == "":
                    maxLength = max(maxLength, currentLength)
                    currentLength = 0
                elif slot in studentSched and slot in comparedSched:
                    currentLength += 0.5
                else:
                    maxLength = max(maxLength, currentLength)
                    currentLength = 0
                maxLength = max(maxLength, currentLength)
            allStudentsChunks.append((student.displayName, maxLength,
                                      student.contactDetails, student_id))
        student_id += 1
    return allStudentsChunks

def merge(L1_list: List, L2_list: List):
    mergedList = []
    L1 = deque(L1_list)
    L2 = deque(L2_list)
    while L1 and L2:
        if L1[0][1] > L2[0][1]:
            mergedList.append(L1.popleft())
        else:
            mergedList.append(L2.popleft())
    mergedList.extend(L1)
    mergedList.extend(L2)
    return mergedList

def merge_sort(L):
    if len(L) <= 1:
        return L
    middleIndex = len(L) // 2
    firstHalf = L[:middleIndex]
    secondHalf = L[middleIndex:]
    firstHalf = merge_sort(firstHalf)
    secondHalf = merge_sort(secondHalf)
    return merge(firstHalf, secondHalf)

# API ROUTES

@app.post("/api/create_section")
def api_create_section(newSection : CreateSection):
    """Create a section and match it with a passcode."""
    with SessionLocal() as session:
        passcode = create_passcode()
        while get_section_orm(passcode, session) is not None:
            passcode = create_passcode()
        s = SectionORM(uuid=passcode,
                       sectionName=newSection.sectionName,
                       sectionDetails=newSection.sectionDetails,
                       maxSize=newSection.maxSize)
        session.add(s)
        session.commit()
        return {'passcode': passcode}

@app.post("/api/{passcode}/create_student")
def api_create_student(passcode : str, newStudent : Student):
    """Create a student and match it with a student id."""
    with SessionLocal() as session:
        sorm = get_section_orm(passcode, session)
        if sorm is not None:
            students = get_students_for_section(sorm, session)
            if sorm.maxSize > len(students):
                student_id = len(students)
                som = StudentORM(displayName=newStudent.displayName,
                                 contactDetails=newStudent.contactDetails,
                                 section_id=sorm.id)
                som.schedule = newStudent.schedule
                session.add(som)
                session.commit()
                return {'student_id': student_id}
    return {'result': 'error', 'message': 'Section not found or max size reached'}

@app.get("/api/{passcode}/{student_id}/view_schedule")
def api_view_schedule(passcode : str, student_id : int):
    """Retrieve the schedule of a student of a section."""
    section: Optional[Section] = validate_student_and_get_section(passcode, student_id)
    if section is not None:
        student = section.studentList[student_id]
        return {'schedule': student.schedule}
    return {'result': 'error', 'message': 'Student or section not found'}

@app.post("/api/{passcode}/{student_id}/update_schedule")
def api_update_schedule(passcode : str, student_id : int, update : ScheduleUpdate):
    """Update the schedule of a student of a section."""
    with SessionLocal() as session:
        sorm = get_section_orm(passcode, session)
        if sorm is None:
            return {'result': 'error'}
        students = get_students_for_section(sorm, session)
        if 0 <= student_id < len(students):
            som = students[student_id]
            som.schedule = update.schedule
            session.add(som)
            session.commit()
            return {'result': 'success'}
    return {'result': 'error'}

@app.get("/api/{passcode}/{student_id}/get_classmate_names")
def api_get_studentlist(passcode : str, student_id : int):
    """Retrieve all display names of classmates of the specified student."""
    with SessionLocal() as session:
        sorm = get_section_orm(passcode, session)
        if sorm is not None:
            students = get_students_for_section(sorm, session)
            if 0 <= student_id < len(students):
                studentList = [s.displayName for idx, s in enumerate(students) if idx != student_id]
                return {'studentList': studentList}
    return {'result': 'error', 'message': 'Section not found or invalid student ID'}

@app.get("/api/{passcode}/verify")
def api_verify_passcode(passcode : str):
    """Verify if passcode exists in the database."""
    with SessionLocal() as session:
        return {'result': get_section_orm(passcode, session) is not None}

@app.get("/api/{passcode}/{student_id}/group_cumulative")
def api_group_cumulative(passcode : str, student_id : int):
    """Retrieve a ranked list of classmates of the specified student."""
    section: Optional[Section] = validate_student_and_get_section(passcode, student_id)
    if section is not None:
        student = section.studentList[student_id]
        similarSchedules = similar_hours_cumulative(student, section)
        return {"data": merge_sort(similarSchedules)}
    return {'result': 'error', 'message': 'Student or section not found'}

@app.get("/api/{passcode}/{student_id}/group_consecutive")
def api_group_consecutive(passcode : str, student_id : int):
    """Retrieve a ranked list of classmates of the specified student."""
    section: Optional[Section] = validate_student_and_get_section(passcode, student_id)
    if section is not None:
        student = section.studentList[student_id]
        similarSchedules = similar_hours_consecutive(student, section)
        return {"data": merge_sort(similarSchedules)}
    return {'result': 'error', 'message': 'Student or section not found'}

@app.get("/api/{passcode}/{student_id}/schedule_intersect/{classmate_id}")
def api_check_schedule_intersection(passcode : str, student_id : int, classmate_id : int):
    with SessionLocal() as session:
        sorm = get_section_orm(passcode, session)
        if sorm is None:
            return {'result': 'error', 'message': 'Section not found'}
        students = get_students_for_section(sorm, session)
        if 0 <= student_id < len(students) and 0 <= classmate_id < len(students):
            studentA = students[student_id]
            studentB = students[classmate_id]
            studentASched = studentA.schedule
            studentBSched = studentB.schedule
            if studentASched and studentBSched:
                intersections = studentASched.intersection(studentBSched)
                studentADiff = studentASched.difference(studentBSched)
                studentBDiff = studentBSched.difference(studentASched)
                return {"intersections": intersections, 
                        "studentADiff": studentADiff, 
                        "studentBDiff": studentBDiff}
    return {'result': 'error', 'message': 'Invalid student or classmate ID'}

# WEB ROUTES

@app.get("/", response_class=HTMLResponse)
def home(request : Request):
    """View home screen."""
    if templates:
        return templates.TemplateResponse("home.html", {"request": request})
    return HTMLResponse("<h1>Templates not available</h1>")

@app.get("/create_section", response_class=HTMLResponse)
def create_section(request : Request):
    """View create section screen."""
    if templates:
        return templates.TemplateResponse("create_section.html", {"request": request})
    return HTMLResponse("<h1>Templates not available</h1>")

@app.get("/{passcode}/create_student", response_class=HTMLResponse)
def create_student(request : Request, passcode : str):
    """View create student screen."""
    with SessionLocal() as session:
        if get_section_orm(passcode, session) is not None:
            if templates:
                return templates.TemplateResponse("create_student.html", {"request": request, 
                                                                         "passcode": passcode})
    return templates.TemplateResponse("error_page.html", {"request": request}) if templates else HTMLResponse("<h1>Error</h1>")

@app.get("/{passcode}/{student_id}", response_class=HTMLResponse)
def view_section(request : Request, passcode : str, student_id : int):
    """View schedule-table and section screen."""
    section: Optional[Section] = validate_student_and_get_section(passcode, student_id)
    if section is not None and templates:
        return templates.TemplateResponse("view_section.html", {"request": request, 
                                                               "passcode": passcode, 
                                                               "student_id": student_id,
                                                               "displayName": section.studentList[student_id].displayName,
                                                               "className": section.sectionName,
                                                               "classDescription": section.sectionDetails})
    return templates.TemplateResponse("error_page.html", {"request": request}) if templates else HTMLResponse("<h1>Error</h1>")

@app.get("/{passcode}/{student_id}/view_group", response_class=HTMLResponse)
def view_group(request : Request, passcode : str, student_id : int):
    """View options for groupings."""
    section: Optional[Section] = validate_student_and_get_section(passcode, student_id)
    if section is not None:
        student = section.studentList[student_id]
        if not student.schedule:
            return RedirectResponse(f"/{passcode}/{student_id}")
        if templates:
            return templates.TemplateResponse("view_groupmates.html", {"request": request, 
                                                                       "passcode": passcode, 
                                                                       "student_id": student_id})
    return templates.TemplateResponse("error_page.html", {"request": request}) if templates else HTMLResponse("<h1>Error</h1>")

@app.exception_handler(404)
def catch_404_errors(request : Request, exc: HTTPException):
    """Catch all for non-existent pages."""
    return RedirectResponse("/")

@app.exception_handler(RequestValidationError)
def catch_errors(request : Request, exc: RequestValidationError):
    """Catch all for unprocessable pages."""
    return RedirectResponse("/")