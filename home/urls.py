from django.urls import path
from .import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[
    ##################### ADMIN URLS #####################
    path('', views.signingAdmin, name='signingAdmin'),
    path('homeAdmin', views.homeAdmin, name='homeAdmin'),
    path('', views.logoutAdmin, name='logoutAdmin'),
    path('categoryVoting', views.categoryVoting, name='categoryVoting'),
    path('viewVots/<uuid:category_id>/', views.viewVots, name='viewVots'),
    path('urvoting/', views.ussdapp, name='ussd')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)