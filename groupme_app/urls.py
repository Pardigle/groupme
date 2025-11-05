from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('join_class', views.join_class, name='join_class'),
    path('create_schedule', views.create_schedule, name='create_schedule'),
    path('student_list', views.student_list, name='student_list'), # needs pk
]