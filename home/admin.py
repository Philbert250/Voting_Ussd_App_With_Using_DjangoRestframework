from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Student)
admin.site.register(Category)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Voters)