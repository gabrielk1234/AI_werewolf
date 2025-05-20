from django.contrib import admin
from django.urls import path,include
from app_werewolfkill import views
urlpatterns = [
    path('',views.home,name='home')
]
