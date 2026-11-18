from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import CustomUser


@login_required
def home_view(request):
    """Send each user to the dashboard for their role."""
    if request.user.role == CustomUser.Role.ADMIN:
        return redirect('dashboard:admin_panel')
    return redirect('dashboard:student_home')


@role_required(CustomUser.Role.STUDENT)
def student_home_view(request):
    return render(request, 'dashboard/home.html')


@role_required(CustomUser.Role.ADMIN)
def admin_panel_view(request):
    students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT)
    return render(request, 'dashboard/admin_panel.html', {
        'student_count': students.count(),
        'recent_students': students.order_by('-date_joined')[:10],
    })
