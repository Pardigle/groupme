from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException, RequestValidationError
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

@app.post("/api/create_section")
def api_create_section(newSection : Section):
    """Create a section and match it with a passcode."""
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
        studentList = [i.displayName for stud_id, i in enumerate(section.studentList)
                       if stud_id != student_id]
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
        sortedSimilarSchedules = merge_sort(similarSchedules)
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
        sortedSimilarSchedules = merge_sort(similarSchedules)
        return {"data":sortedSimilarSchedules}
    
@app.get("/api/{passcode}/{student_id}/schedule_intersect/{classmate_id}")
def api_check_schedule_intersection(passcode : str, student_id : int, classmate_id : int):
    if validate_student(passcode, student_id) and validate_student(passcode, classmate_id):
        section = db[passcode]
        studentA = section.studentList[student_id]
        studentB = section.studentList[classmate_id]
        studentASched = studentA.schedule
        studentBSched = studentB.schedule
        intersections = studentASched.intersection(studentBSched)
        studentADiff = studentASched.difference(studentBSched)
        studentBDiff = studentBSched.difference(studentASched)
        return {"intersections":intersections, 
                "studentADiff":studentADiff, 
                "studentBDiff":studentBDiff}

# Helper Functions

def validate_student(passcode : str, student_id : int):
    """Verify student-section pair."""
    if passcode in db:
        if student_id in range(len(db[passcode].studentList)):
            return True
    return False

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    """Retrieve total similar schedule between a student and their classmates.

    Returns a list 'similarHours' of tuples containing: 
    (classmateDisplayName, classmateSimilarHours, classmateContactDetails)
    """
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
    """Retrieve length of longest consecutive similar time between a student and
    their classmates.

    Returns a list 'similarHours' of tuples containing: 
    (classmateDisplayName, classmateConsecutiveHours, classmateContactDetails)
    """
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
                    maxLength = max(maxLength,currentLength)
                    currentLength =0
                elif slot in studentSched and slot in comparedSched:
                    currentLength += 0.5
                else:
                    maxLength = max(maxLength,currentLength)
                    currentLength =0
                maxLength = max(maxLength,currentLength)
            allStudentsChunks.append((student.displayName, maxLength,
                                      student.contactDetails, student_id))
        student_id += 1
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

def merge_sort(L):
    """Merge sort implementation."""
    if len(L) <= 1:
        return L
    else:
        middleIndex = len(L) // 2
        firstHalf = L[:middleIndex]
        secondHalf = L[middleIndex:]
        firstHalf = merge_sort(firstHalf)
        secondHalf = merge_sort(secondHalf)
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
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = student.schedule
        if not schedule:
            return RedirectResponse(f"/{passcode}/{student_id}")
        return templates.TemplateResponse("view_groupmates.html", {"request": request, 
                                                            "passcode": passcode, 
                                                            "student_id": student_id})
    return templates.TemplateResponse("error_page.html", {"request":request})

@app.exception_handler(404)
def catch_404_errors(request : Request, exc: HTTPException):
    """Catch all for non-existent pages."""
    return RedirectResponse("/")

@app.exception_handler(RequestValidationError)
def catch_errors(request : Request, exc: RequestValidationError):
    """Catch all for unprocessable pages."""
    return RedirectResponse("/")

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

if __name__ == "__main__":
    uvicorn.run(app)