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