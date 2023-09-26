from django.urls import path
from .import views
from .views import *
from django.conf import settings

urlpatterns =[
    path('urvoting/', views.ussdapp, name='ussd')
]