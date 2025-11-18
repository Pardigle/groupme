from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from passcodes import create_passcode

# Theoretical Database
db = {}

# Models
class Student(BaseModel):
    displayName : str
    contactDetails : str
    schedule : set[str]

class Section(BaseModel):
    sectionName : str
    sectionDetails : str
    maxSize : int
    studentDict : dict[int, Student] = {}

# API
api = FastAPI()

@api.post("/create_section")
def create_section(newSection : Section):
    passcode = create_passcode()
    db[passcode] = newSection
    return {'passcode':passcode}

@api.post("/{passcode}/create_student")
def create_account(passcode : str, newStudent : Student):
    if passcode in db:
        studentDict = db[passcode].studentDict
        student_id = len(studentDict)
        studentDict[student_id] = newStudent
        return {'student_id':student_id}

@api.get("/{passcode}")
def view_section(passcode : str):
    if passcode in db:
        return db[passcode].model_dump()
    
@api.get("/{passcode}/{student_id}/group_cumulative")
def group_cumulative(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentDict[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return dict(sortedSimilarSchedules)

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

def rank_schedules(similarHours): #mergesorted
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