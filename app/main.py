from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passcodes import create_passcode
from models import Student, Section, ScheduleUpdate
import uvicorn

app = FastAPI()

app.mount("/logo-assets", StaticFiles(directory="templates/logo"), name="static")

templates = Jinja2Templates(directory="templates")

db = {}

# BACKEND

@app.get("/api/{passcode}")
def api_view_section(passcode : str):
    if passcode in db:
        return db[passcode].model_dump()

@app.post("/api/create_section")
def api_create_section(newSection : Section):
    passcode = create_passcode()
    db[passcode] = newSection
    return {'passcode':passcode}

@app.post("/api/{passcode}/create_student")
def api_create_student(passcode : str, newStudent : Student):
    if passcode in db:
        studentList = db[passcode].studentList
        student_id = len(studentList)
        studentList.append(newStudent)
        return {'student_id':student_id}

@app.get("/api/{passcode}/{student_id}/view_schedule")
def api_view_schedule(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = student.schedule
        return {'schedule':schedule}

@app.post("/api/{passcode}/{student_id}/update_schedule")
def api_update_schedule(passcode : str, student_id : int, update : ScheduleUpdate):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = update.schedule
        student.schedule = set(schedule)
        return {'result':'success'}
    return {'result':'error'}


@app.get("/api/{passcode}/verify")
def api_verify_passcode(passcode : str):
    if passcode in db:
        return {'result':'success'}
    return {'result':'error'}
    
@app.get("/api/{passcode}/{student_id}/group_cumulative")
def api_group_cumulative(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return {"data":sortedSimilarSchedules}

def validate_student(passcode : str, student_id : int):
    if passcode in db:
        if student_id in range(len(db[passcode].studentList)):
            return True
    return False

# ALGORITHMS

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    similarHours = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    student_id = 0
    for student in rankingList:
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append((student.displayName, len(similarSched) * 0.5, student.contactDetails))
    return similarHours

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
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/create_section", response_class=HTMLResponse)
def create_section(request : Request):
    return templates.TemplateResponse("create_section.html", {"request": request})

@app.get("/{passcode}/create_student", response_class=HTMLResponse)
def create_student(request : Request, passcode : str):
    return templates.TemplateResponse("create_student.html", {"request": request, 
                                                              "passcode":passcode})

@app.get("/{passcode}/{student_id}")
def view_section(request : Request, passcode : str, student_id : int):
    displayName = ""
    className = ""
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

@app.get("/{passcode}/{student_id}/view_group")
def view_group(request : Request, passcode : str, student_id : int):
    return templates.TemplateResponse("view_groupmates.html", {"request": request, 
                                                            "passcode": passcode, 
                                                            "student_id": student_id})

if __name__ == "__main__":
    uvicorn.run(app)