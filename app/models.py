from pydantic import BaseModel

class Student(BaseModel):
    displayName : str
    contactDetails : str
    schedule : set[str] = {}

class Section(BaseModel):
    sectionName : str
    sectionDetails : str
    maxSize : int
    studentList : list[Student] = []

class ScheduleUpdate(BaseModel):
    schedule: list[str]