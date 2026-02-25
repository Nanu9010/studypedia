from django.shortcuts import render

# Create your views here.
# ===== core/views.py =====
from django.shortcuts import render
from django.http import JsonResponse
from notes.models import Note
from university.models import University, Degree, Branch
from django.db.models import Count
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# core/views.py

from university.models import University

def home(request):
    stats = {
        'total_notes': Note.objects.filter(is_active=True).count(),
        'total_papers': Paper.objects.filter(is_active=True).count(),  # Replaced total_subjects
        'total_universities': University.objects.filter(is_active=True).count(),
        'total_downloads': 0,  # Replace with actual logic (e.g., from Order model)
    }
    featured_notes = Note.objects.filter(is_active=True).order_by('-created_at')[:3]
    featured_papers = Paper.objects.filter(is_active=True).order_by('-created_at')[:3]
    return render(request, 'core/home.html', {
        'stats': stats,
        'featured_notes': featured_notes,
        'featured_papers': featured_papers,
    })



def about(request):
    """About page"""
    return render(request, 'core/about.html')


def cascade_filters_api(request):
    """API for cascading filters (University -> Degree -> Branch -> Semester -> Subject)"""
    filter_type = request.GET.get('type')
    parent_id = request.GET.get('parent_id')

    if filter_type == 'degrees' and parent_id:
        items = Degree.objects.filter(university_id=parent_id, is_active=True).values('id', 'name')
    elif filter_type == 'branches' and parent_id:
        items = Branch.objects.filter(degree_id=parent_id, is_active=True).values('id', 'name')

    else:
        items = []

    return JsonResponse({'items': list(items)})






# core/views.py (advanced search)
from django.shortcuts import render
from django.db.models import Q
from notes.models import Note
from papers.models import Paper

def search_view(request):
    query = request.GET.get('q', '')
    university = request.GET.get('university', '')
    year = request.GET.get('year', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort = request.GET.get('sort', 'title')
    view = request.GET.get('view', 'grid')

    notes = Note.objects.all()
    papers = Paper.objects.all()

    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(description__icontains=query))
        papers = papers.filter(Q(subject__name__icontains=query) | Q(year__icontains=query))

    # Apply filters
    if university:
        notes = notes.filter(subject__branch__degree__university__id=university)
        papers = papers.filter(subject__branch__degree__university__id=university)

    if year:
        notes = notes.filter(year=year)
        papers = papers.filter(year=year)
    if price_min:
        notes = notes.filter(price__gte=price_min)
        papers = papers.filter(price__gte=price_min)  # Assume price field added to Paper/Note
    if price_max:
        notes = notes.filter(price__lte=price_max)
        papers = papers.filter(price__lte=price_max)

    # Sorting
    if sort == 'price_asc':
        notes = notes.order_by('price')
        papers = papers.order_by('price')
    elif sort == 'price_desc':
        notes = notes.order_by('-price')
        papers = papers.order_by('-price')
    elif sort == 'year_asc':
        notes = notes.order_by('year')
        papers = papers.order_by('year')
    elif sort == 'year_desc':
        notes = notes.order_by('-year')
        papers = papers.order_by('-year')

    context = {
        'notes': notes,
        'papers': papers,
        'view': view,
        'universities': University.objects.all(),
        'query': query,
        'university': university,

        'year': year,
        'price_min': price_min,
        'price_max': price_max,
        'sort': sort,
    }
    return render(request, 'core/search.html', context)