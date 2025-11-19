from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passcodes import create_passcode
from models import Student, Section
import uvicorn

api = FastAPI()

api.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

db = {}

# ROUTES

@api.get("/", response_class=HTMLResponse)
def home(request : Request):
    return templates.TemplateResponse("home.html", {"request": request})

@api.get("/create_section", response_class=HTMLResponse)
def create_section(request : Request):
    return templates.TemplateResponse("create_section.html", {"request": request})

@api.get("{passcode}/create_student", response_class=HTMLResponse)
def create_student(request : Request):
    return templates.TemplateResponse("create_student.html", {"request": request})

@api.get("{passcode}/{student_id}")
def view_section(request : Request):
    return templates.TemplateResponse("view_section.html", {"request": request})

@api.get("{passcode}/{student_id}/view_group")
def view_group(request : Request):
    return templates.TemplateResponse("view_groupmates.html", {"request": request})

# BACKEND

@api.post("/api/create_section")
def api_create_section(newSection : Section):
    passcode = create_passcode()
    db[passcode] = newSection
    return {'passcode':passcode}

@api.post("/api/{passcode}/create_student")
def api_create_student(passcode : str, newStudent : Student):
    if passcode in db:
        studentDict = db[passcode].studentDict
        student_id = len(studentDict)
        studentDict[student_id] = newStudent
        return {'student_id':student_id}

@api.get("/api/{passcode}/verify")
def api_verify_passcode(passcode : str):
    if passcode in db:
        return {'result':'success'}
    return {'result':'error'}
    

@api.get("/api/{passcode}")
def api_view_section(passcode : str):
    if passcode in db:
        return db[passcode].model_dump()
    
@api.get("/api/{passcode}/{student_id}/group_cumulative")
def api_group_cumulative(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentDict[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return sortedSimilarSchedules

def validate_student(passcode : str, student_id : int):
    if passcode in db:
        if student_id in db[passcode].studentDict:
            return True
    return False

# ALGORITHMS

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    similarHours = []
    rankingList = currentSection.studentDict
    studentSched = currentStudent.schedule
    for student_id in rankingList:
        student = rankingList[student_id]
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append((student_id, len(similarSched) * 0.5))
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
    
if __name__ == "__main__":
    uvicorn.run(api)