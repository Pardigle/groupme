from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Theoretical Database
db = {}

# Models
class Student(BaseModel):
    displayName : str
    contactDetails : str
    schedule : set[str]

class Section(BaseModel):
    passcode : str
    sectionName : str
    sectionDetails : str
    maxSize : int
    studentDict : dict[int, Student]

# API
api = FastAPI()

@api.post("/create_section")
def create_section(newSection : Section):
    db[len(db)] = newSection
    return {'message':'section created'}

@api.post("/{section_id}/create_student")
def create_account(section_id : int, newStudent : Student):
    if validate_section(section_id):
        studentDict = db[section_id].studentDict
        studentDict[len(studentDict)] = newStudent
        return {'message':'student created.'}

@api.get("/{section_id}")
def view_section(section_id : int):
    if validate_section(section_id):
        return db[section_id]
    
@api.get("/{section_id}/{student_id}/group_cumulative")
def group_cumulative(section_id : int, student_id : int):
    if validate_student(section_id, student_id):
        section = db[section_id]
        student = section.studentDict[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = rank_schedules(similarSchedules)
        return dict(sortedSimilarSchedules)
    
    
def validate_section(section_id : int):
    if section_id in db:
        return True
    return False

def validate_student(section_id : int, student_id : int):
    if section_id in db:
        if student_id in db[section_id].studentDict:
            return True
    return False

# ALGORITHMS

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    similarHours = list[list[int, str]] #total number of similar free hours per student. key is username, value is no. of free hours
    rankingList = currentSection.studentDict
    studentSched = currentStudent.schedule
    for index, student in enumerate(rankingList):
        if student != currentStudent:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append(index + 1, len(similarSched) * 0.5) #format: (student_id, similarHours)
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