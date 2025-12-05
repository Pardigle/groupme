import unittest
from unittest.mock import patch
from models import Student, Section, ScheduleUpdate

db = {}

class GroupMeUnitTests(unittest.TestCase):

    def setUp(self):
        
        self.passcode = "ABC123"
        self.section = Section(sectionName="Krusty Krabs", maxSize=4)

        self.studentA = Student(displayName="Mr. Krabs",
                                contactDetails="Meet me at Krusty Krabs.",
                                schedule={
                                    "0-0800-0830", "0-0830-0900", "0-0900-0930"
                                })
        self.studentB = Student(displayName="Spongebob",
                                contactDetails="Hello, I am Spongebob.",
                                schedule={
                                    "0-0800-0830", "0-0830-0900", "0-0900-0930"
                                })
        self.studentC = Student(displayName="Squidward",
                                contactDetails="Go away.",
                                schedule={
                                    "0-0800-0830", "0-0900-0930", "0-1000-1030"
                                })
        self.studentD = Student(displayName="Patrick Star",
                                contactDetails="I'm in my rock.",
                                schedule={
                                    "0-0800-0830", "0-0900-0930", "0-1000-1030"
                                })

        db[self.passcode] = self.section
        self.section.studentList.append(self.studentA)
        self.section.studentList.append(self.studentB)
        self.section.studentList.append(self.studentC)
        self.section.studentList.append(self.studentD)

    def test_validate_student_success(self):
        self.assertTrue(validate_student(self.passcode, 0))
        self.assertTrue(validate_student(self.passcode, 2))
    
    def test_validate_student_fail_passcode(self):
        self.assertFalse(validate_student("CHUM12", 0))
        self.assertFalse(validate_student("GORP36", 2))
    
    def test_validate_student_fail_student_id(self):
        self.assertFalse(validate_student(self.passcode, 4)) 
        self.assertFalse(validate_student(self.passcode, -3))
    
    def test_merge_sort(self):
        data = [("D", 0.5), ("C", 1.5), ("B", 3), ("A", 4.5)]
        expected_sort = [("A", 4.5), ("B", 3), ("C", 1.5), ("D", 0.5)]
        self.assertEqual(merge_sort(data), expected_sort)
        self.assertEqual(merge_sort([]), [])
    
    def test_similar_hours_cumulative(self):
        result = similar_hours_cumultative(self.studentA, self.section)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][1], 1.5) 
        self.assertEqual(result[1][1], 1.0)
        self.assertEqual(result[2][1], 1.0)

    def test_similar_hours_consecutive(self):
        result = similar_hours_consecutive(self.studentA, self.section)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][1], 1.5)
        self.assertEqual(result[1][1], 0.5)
        self.assertEqual(result[2][1], 0.5)

    def test_api_create_student_success(self):
        self.section.studentList.pop() 
        new_student = self.studentD
        response = api_create_student(self.passcode, new_student)
        self.assertEqual(response, {'student_id': 3})
        self.assertEqual(len(db[self.passcode].studentList), 4) 
    
    def test_api_create_student_fail_max_size(self):
        new_student = Student(displayName="Sandy Cheeks",
                            contactDetails="Yeehaw!",
                            schedule={"0-0800-0830"})
        response = api_create_student(self.passcode, new_student)
        self.assertIsNone(response)
        self.assertEqual(len(db[self.passcode].studentList), 4)

    def test_api_view_schedule_success(self):
        response = api_view_schedule(self.passcode, 0)
        self.assertEqual(response['schedule'], {"0-0800-0830", "0-0830-0900", "0-0900-0930"})
    
    def test_api_view_schedule_fail_student_id(self):
        response = api_view_schedule(self.passcode, 99)
        self.assertIsNone(response)
    
    def test_api_update_schedule_success(self):
        new_schedule = ["0-0800-0830", "0-0930-1000", "0-1030-1100"]
        update_data = ScheduleUpdate(schedule=new_schedule)
        response = api_update_schedule(self.passcode, 1, update_data)
        self.assertEqual(response, {'result': 'success'}) 
        self.assertEqual(db[self.passcode].studentList[1].schedule, set(new_schedule))

    def test_api_get_studentList_success(self):
        response = api_get_studentlist(self.passcode, 1)
        self.assertEqual(response['studentList'], ['Mr. Krabs'])

    def test_api_verify_passcode(self):
        self.assertEqual(api_verify_passcode(self.passcode), {'result': True})
        self.assertEqual(api_verify_passcode("GLORBS"), {'result': False})
    
    def test_api_group_cumulative_ranking(self):
        response = api_group_cumulative(self.passcode, 0)
        
        expected_result = [
            ('Spongebob', 1.5, 'Hello, I am Spongebob.', 1),
            ('Patrick Star', 1.0, "I'm in my rock.", 3),
            ('Squidward', 1.0, 'Go away.', 2)
        ]
        self.assertEqual(response['data'], expected_result)

    def test_api_group_consecutive_ranking(self):
        response = api_group_consecutive(self.passcode, 0)
        
        expected_result = [
            ('Spongebob', 1.5, 'Hello, I am Spongebob.', 1),
            ('Patrick Star', 0.5, "I'm in my rock.", 3),
            ('Squidward', 0.5, 'Go away.', 2)
        ]
        self.assertEqual(response['data'], expected_result)

#Copy-pasted relevant functions to test, which use global variable db.

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

# START OF UNIT TESTS 

def validate_student(passcode : str, student_id : int):
    if passcode in db:
        if 0 <= student_id < len(db[passcode].studentList):
            return True
    return False

def similar_hours_cumultative(currentStudent: Student, currentSection: Section):
    similarHours = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    try:
        current_student_id = rankingList.index(currentStudent)
    except ValueError:
        current_student_id = -1 

    for student_id, student in enumerate(rankingList):
        if student_id != current_student_id:
            comparedSched = student.schedule
            similarSched = studentSched.intersection(comparedSched)
            similarHours.append((student.displayName, len(similarSched) * 0.5,
                                 student.contactDetails, student_id))
    return similarHours

def similar_hours_consecutive(currentStudent: Student, currentSection: Section):
    allStudentsChunks = []
    rankingList = currentSection.studentList
    studentSched = currentStudent.schedule
    try:
        current_student_id = rankingList.index(currentStudent)
    except ValueError:
        current_student_id = -1

    for student_id, student in enumerate(rankingList):
        if student_id != current_student_id:
            comparedSched = student.schedule
            currentLength = 0
            maxLength = 0
            for slot in ALLPOSSIBLETIMES:
                if slot == "":
                    maxLength = max(maxLength,currentLength)
                    currentLength = 0
                elif slot in studentSched and slot in comparedSched:
                    currentLength += 0.5
                else:
                    maxLength = max(maxLength,currentLength)
                    currentLength = 0
            maxLength = max(maxLength,currentLength)
            allStudentsChunks.append((student.displayName, maxLength,
                                      student.contactDetails, student_id))
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
    if len(L) <= 1:
        return L
    else:
        middleIndex = len(L) // 2
        firstHalf = L[:middleIndex]
        secondHalf = L[middleIndex:]
        firstHalf = merge_sort(firstHalf)
        secondHalf = merge_sort(secondHalf)
        return merge(firstHalf, secondHalf)

def api_create_student(passcode : str, newStudent : Student):
    if passcode in db:
        section = db[passcode]
        studentList = section.studentList
        if section.maxSize > len(studentList):
            student_id = len(studentList)
            studentList.append(newStudent)
            return {'student_id':student_id}

def api_view_schedule(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = student.schedule
        return {'schedule':schedule}

def api_update_schedule(passcode : str, student_id : int, update : ScheduleUpdate):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        schedule = update.schedule
        student.schedule = set(schedule)
        return {'result':'success'}
    return {'result':'error'}

def api_get_studentlist(passcode : str, student_id : int):
    if passcode in db:
        section = db[passcode]
        studentList = [i.displayName for i in section.studentList[:student_id:]]
        return {'studentList': studentList}

def api_verify_passcode(passcode : str):
    if passcode in db:
        return {'result':True}
    return {'result':False}

def api_group_cumulative(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        similarSchedules = similar_hours_cumultative(student, section)
        sortedSimilarSchedules = merge_sort(similarSchedules)
        return {"data":sortedSimilarSchedules}
    
def api_group_consecutive(passcode : str, student_id : int):
    if validate_student(passcode, student_id):
        section = db[passcode]
        student = section.studentList[student_id]
        similarSchedules = similar_hours_consecutive(student, section)
        sortedSimilarSchedules = merge_sort(similarSchedules)
        return {"data":sortedSimilarSchedules}

if __name__ == "__main__":
    unittest.main()