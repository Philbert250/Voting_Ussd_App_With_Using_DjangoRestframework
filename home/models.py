from django.db import models
import uuid

# Create your models here.

class Student(models.Model):
    studentId = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    regNumber  = models.CharField(max_length=255)
    name  = models.CharField(max_length=255)
    department  = models.CharField(max_length=255)
    def __str__(self):
        return self.regNumber

class Category(models.Model):
    categoryId = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    categoryName  = models.CharField(max_length=255)
    def __str__(self):
        return self.categoryName

class Candidate(models.Model):
    candidateId = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return str(self.student) 
    

class Vote(models.Model):
    voteId = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    candidate = models.ForeignKey(Candidate, null=True, blank=True, on_delete=models.SET_NULL)
    vots  = models.CharField(max_length=255)
    def __str__(self):
        return str(self.student) 
