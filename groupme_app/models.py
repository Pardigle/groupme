from django.db import models

class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    displayName = models.CharField(max_length=100)
    contactDetails = models.CharField(max_length=100)
    userSchedule = models.JSONField(default=set)

    def get_username(self):
        return self.username

    def get_schedule(self):
        return self.userSchedule

class Section(models.Model):
    passcode = models.CharField(max_length=100)
    sectionName = models.CharField(max_length=100)
    sectionDetails = models.CharField(max_length=200)
    maxSize = models.IntegerField(default=2)
    studentList = models.ManyToManyField(User)

    def get_studentList(self):
        return self.studentList

    def add_student(self, student:User):
        if len(self.studentList) < self.maxSize:
            if student not in self.studentList:
                self.studentList.append(student)
                print(f"Student {student.get_username()} added")
            else:
                print(f"User {student.get_username()} is already in this class")
        else:
            print("CLass is full")

# References:
# MANYTOMANYFIELD: https://docs.djangoproject.com/en/5.2/topics/db/examples/many_to_many/
# JSONFIELD: https://docs.djangoproject.com/en/5.2/ref/models/fields



# PLACING THE SIMILAR HOUR FINDING/SORTING HERE FOR NOW
'''
def find_similar_hours(currentUser:User, currentSection:Section):
  similarHours = [] #total number of similar free hours per student. key is username, value is no. of free hours
  rankingList = currentSection.get_studentList().copy()
  rankingList.remove(currentUser)
  print(rankingList)

  for student in rankingList:
    studentSchedule = student.get_schedule()
    similarHours.append((len(currentUser.get_schedule().intersection(studentSchedule)) * 0.5, student.get_username()))

  return similarHours



def merge(L1, L2):
  mergedList = []

  while len(L1) != 0 and len(L2) != 0:
    if L1[0][0] > L2[0][0]:
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
    print(hoursList)

    firstHalf = hoursList[:middleIndex]
    secondHalf = hoursList[middleIndex:]
    firstHalf = rank_schedules(firstHalf)
    secondHalf = rank_schedules(secondHalf)
    return merge(firstHalf, secondHalf)
'''

# TEST RUN
'''
a = User("userA", "dnA", "123A", {"M-1100-1130", "M-1130-1200", "M-1200-1230", "TH-1530-1600"})
b = User("userB", "dnB", "234B", {"M-1100-1130", "M-1130-1200", "M-1200-1230", "TH-1530-1600", "F-0930-1100"})
c = User("userC", "dnC", "345C", {"M-1100-1130", "M-1130-1200", "M-1200-1230"})
d = User("userD", "dnD", "456D", {"M-1100-1130", "M-1130-1200"})
e = User("userE", "dnE", "567E", {"M-1100-1130", "M-1130-1200"})

test = Section("Test section", "12345", "Test", 4)
test.add_student(a)
test.add_student(d)
test.add_student(d)
test.add_student(b)
test.add_student(c)
test.add_student(e)

print(a.get_schedule())

print(test.get_studentList())

print("")
print(find_similar_hours(a,test))
print("")
rank_schedules(find_similar_hours(a,test))
'''