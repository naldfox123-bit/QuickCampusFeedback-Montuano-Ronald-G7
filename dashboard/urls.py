from django.urls import path

from .views import admin_panel_view, home_view, student_home_view

app_name = 'dashboard'

urlpatterns = [
    path('', home_view, name='home'),
    path('student/', student_home_view, name='student_home'),
    path('admin-panel/', admin_panel_view, name='admin_panel'),
]
