from pydantic import BaseModel

class Student(BaseModel):
    """
    Represents a student joined in a section
    
    displayName: The name of student
    contactDetails: Chosen contact details of student
    schedule: Set containing string schedules of student
    """
    displayName : str
    contactDetails : str
    schedule : set[str] = {}

class Section(BaseModel):
    """
    Represents a section in the database

    sectionName: The name of section
    sectionDetails: Details for section
    maxSize: Maximum students under section
    studentList: List of Students joined in section
    """
    sectionName : str
    sectionDetails : str
    maxSize : int
    studentList : list[Student] = []

class ScheduleUpdate(BaseModel):
    """
    Represents a data packet for updating a
    schedule of a student

    schedule: List containing string schedules of update
    """
    schedule: list[str]