from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('enrollment/', views.enrollment_report, name='enrollment_report'),
    path('course-popularity/', views.course_popularity, name='course_popularity'),
    path('lecturer-load/', views.lecturer_load, name='lecturer_load'),
]
