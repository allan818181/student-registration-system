from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    path('', views.enrollment_list, name='enrollment_list'),
    path('approve/<int:pk>/', views.enrollment_approve, name='enrollment_approve'),
    path('register/<int:course_id>/', views.register_course, name='register_course'),
    path('drop/<int:enrollment_id>/', views.drop_course, name='drop_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
]
