# adminapp/views.py
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from accounts.models import User
from ecommerce.models import Order
from university.models import University, Degree, Branch
from papers.models import Paper
from notes.models import Note
from roadmaps.models import Roadmap, Syllabus
# Assume other models as needed
from accounts.views import is_staff


@user_passes_test(is_staff)
def dashboard(request):
    context = {
        'users_count': User.objects.count(),
        'orders_count': Order.objects.count(),
        'universities_count': University.objects.count(),
        'degrees_count': Degree.objects.count(),
        'branches_count': Branch.objects.count(),

        'papers_count': Paper.objects.count(),
        'notes_count': Note.objects.count(),
        'roadmaps_count': Roadmap.objects.count(),
        'syllabi_count': Syllabus.objects.count(),
    }
    return render(request, 'adminapp/dashboard.html', context)