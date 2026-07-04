from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/', views.student_register, name='register'),
    path('login/', views.student_login, name='login'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('course/<str:course_code>/', views.student_course_view, name='student_course_view'),
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/course/<str:course_code>/', views.admin_course_view, name='admin_course_view'),
    path('admin-login/', views.custom_admin_login, name='custom_admin_login'),
    path('staff/course/<str:course_code>/create/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/confirm/', views.confirm_exam_start, name='confirm_exam_start'),
    path('face-check/', views.face_check, name='face_check'),
    path('log-suspicious/', views.log_suspicious, name='log_suspicious'),
    path('course/<str:course_code>/', views.student_course_view, name='student_coures')


]
