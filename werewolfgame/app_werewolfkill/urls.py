from django.contrib import admin
from django.urls import path,include
from app_werewolfkill import views
urlpatterns = [
    path('',views.home,name='home'),
    # read pdf
    path('api_read_pdf/',views.api_read_pdf),
    # delete log
    path('delete-log/',views.delete_log)
]
