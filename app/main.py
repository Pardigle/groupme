from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from passcodes import create_passcode
from models import Student, Section, ScheduleUpdate
import uvicorn
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR/"templates"/"logo"

app.mount("/logo-assets", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR/"templates"))

db = {}

@app.get("/api/{passcode}")
def api_view_section(passcode : str):
    """Retrieve all attributes of a section."""
    if passcode in db:
        return db[passcode].model_dump()

@app.post("/api/create_section")
def api_create_section(newSection : Section):
    """Create a section and match it with a passcode."""
    while True:
        passcode = create_passcode()
        if passcode not in db:
            db[passcode] = newSection
            return {'passcode':passcode}

@app.post("/api/{passcode}/create_student")
def api_create_student(passcode : str, newStudent : Student):
    """Create a student and match it with a student id."""
    if passcode in db:
        section = db[passcode]
        studentList = section.studentList
        if section.maxSize > len(studentList):
            student_id = len(studentList)
            studentList.append(newStudent)
            return {'student_id':student_id}

@app.get("/api/{passcode}/{student_id}/view_schedule")
def api_view_schedule(passcode : str, student_id : int):
    """Retrieve the schedule of a student of a section."""
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = student.schedule
        return {'schedule':schedule}

@app.post("/api/{passcode}/{student_id}/update_schedule")
def api_update_schedule(passcode : str, student_id : int, update : ScheduleUpdate):
    """Update the student of a student of a section."""
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = update.schedule
        student.schedule = set(schedule)
        return {'result':'success'}
    return {'result':'error'}

@app.get("/api/{passcode}/{student_id}/get_classmate_names")
def api_get_studentlist(passcode : str, student_id : int):
    """Retrieve all display names of classmates of the specified student."""
    if passcode in db:
        section = db[passcode]
        studentList = [i.displayName for i in section.studentList[:student_id:]]
        return {'studentList': studentList}

@app.get("/api/{passcode}/verify")
def api_verify_passcode(passcode : str):
    """Verify if passcode exists in the database."""
    if passcode in db:
        return {'result':'success'}
    return {'result':'error'}
    
@app.get("/api/{passcode}/{student_id}/group_cumulative")
def api_group_cumulative(passcode : str, student_id : int):
    """Retrieve a ranked list of classmates of the specified student.
    
    Ranks classmates based on total intersections of schedule with
    the specified student.
    """
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return {"data":sortedSimilarSchedules}
    
@app.get("/api/{passcode}/{student_id}/group_consecutive")
def api_group_consecutive(passcode : str, student_id : int):
    """Retrieve a ranked list of classmates of the specified student.
    
    Ranks classmates based on largest chunk of similar schedule with
    the specified student.
    """
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        similarSchedules = similar_hours_consecutive(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return {"data":sortedSimilarSchedules}

def validate_student(passcode : str, student_id : int):
    """Verify student-section pair."""
    if passcode in db:
        if student_id in range(len(db[passcode].studentList)):
            return True
    return False

# ALGORITHMS

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    """Retrieve total similar schedule between a student and their classmates.

    Returns a list 'similarHours' of tuples containing: 
    (classmateDisplayName, classmateSimilarHours, classmateContactDetails)
    """
    similarHours = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    for student in rankingList:
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append((student.displayName, len(similarSched) * 0.5, student.contactDetails))
    return similarHours

def similar_hours_consecutive(currentStudent: Student, currentSection: Section):
    """Retrieve length of longest consecutive similar time between a student and
    their classmates.

    Returns a list 'similarHours' of tuples containing: 
    (classmateDisplayName, classmateConsecutiveHours, classmateContactDetails)
    """
    allStudentsChunks = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    for student in rankingList:
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarSched = sorted(list(similarSched))
            maxLength = 0
            if similarSched:
                currentChunkLength = 0.5
                for slotIndex in range(0, len(similarSched)-1):
                    currentDay, currentStart, currentEnd = similarSched[slotIndex].split("-")
                    nextDay, nextStart, nextEnd = similarSched[slotIndex+1].split("-")
                    if currentDay == nextDay and nextStart == currentEnd:
                        currentChunkLength += 0.5
                    else:
                        if currentChunkLength > maxLength:
                            maxLength = currentChunkLength
                        currentChunkLength = 0.5
                maxLength = max(currentChunkLength, maxLength)
            allStudentsChunks.append((student.displayName, maxLength, student.contactDetails))
    return allStudentsChunks

def merge(L1, L2):
    mergedList = []
    while len(L1) != 0 and len(L2) != 0:
        if L1[0][1] > L2[0][1]:
            mergedList.append(L1[0])
            L1.pop(0)
        else:
            mergedList.append(L2[0])
            L2.pop(0)
    while len(L2) != 0:
        mergedList.append(L2[0])
        L2.pop(0)
    while len(L1) != 0:
        mergedList.append(L1[0])
        L1.pop(0)
    return mergedList

def rank_schedules(similarHours):
    """Mergesort implementation."""
    if len(similarHours) <= 1:
        return similarHours
    else:
        hoursList = similarHours.copy()
        middleIndex = len(hoursList) // 2
        firstHalf = hoursList[:middleIndex]
        secondHalf = hoursList[middleIndex:]
        firstHalf = rank_schedules(firstHalf)
        secondHalf = rank_schedules(secondHalf)
        return merge(firstHalf, secondHalf)
    
# ROUTES

@app.get("/", response_class=HTMLResponse)
def home(request : Request):
    """View home screen."""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/create_section", response_class=HTMLResponse)
def create_section(request : Request):
    """View create section screen."""
    return templates.TemplateResponse("create_section.html", {"request": request})

@app.get("/{passcode}/create_student", response_class=HTMLResponse)
def create_student(request : Request, passcode : str):
    """View create student screen."""
    if passcode in db:
        return templates.TemplateResponse("create_student.html", {"request": request, 
                                                              "passcode":passcode})
    return templates.TemplateResponse("error_page.html", {"request":request})

@app.get("/{passcode}/{student_id}", response_class=HTMLResponse)
def view_section(request : Request, passcode : str, student_id : int):
    """View schedule-table and section screen."""
    if validate_student(passcode, student_id):
        section = db[passcode]
        className = section.sectionName
        classDescription = section.sectionDetails
        displayName = section.studentList[student_id].displayName
        return templates.TemplateResponse("view_section.html", {"request": request, 
                                                            "passcode": passcode, 
                                                            "student_id": student_id,
                                                            "displayName": displayName,
                                                            "className":className,
                                                            "classDescription":classDescription})
    return templates.TemplateResponse("error_page.html", {"request":request})

@app.get("/{passcode}/{student_id}/view_group", response_class=HTMLResponse)
def view_group(request : Request, passcode : str, student_id : int):
    """View options for groupings."""
    if validate_student(passcode, student_id):
        return templates.TemplateResponse("view_groupmates.html", {"request": request, 
                                                            "passcode": passcode, 
                                                            "student_id": student_id})
    return templates.TemplateResponse("error_page.html", {"request":request})

@app.exception_handler(404)
def catch_errors(request : Request, exc: HTTPException):
    """Catch all for non-existent pages."""
    return RedirectResponse("/")

if __name__ == "__main__":
    uvicorn.run(app)