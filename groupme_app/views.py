from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Section

def home(request):
  return render(request, 'groupme_app/home.html')

def join_class(request):
  return render(request, 'groupme_app/join_class.html')

def create_section(request):
  return render(request, 'groupme_app/create_section.html')

def create_schedule(request):
  return render(request, 'groupme_app/create_schedule.html')

def student_list(request):
  return render(request, 'groupme_app/student_list.html')



def similar_hours_cumultative(currentUser:User, currentSection:Section):
  similarHours = [] #total number of similar free hours per student. key is username, value is no. of free hours
  rankingList = currentSection.get_studentList().copy()
  rankingList.remove(currentUser)
  print(rankingList)

  for student in rankingList:
    studentSchedule = student.get_schedule()
    similarHours.append((len(currentUser.get_schedule().intersection(studentSchedule)) * 0.5, student.get_username()))

  return similarHours


# MERGE SORT 
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
