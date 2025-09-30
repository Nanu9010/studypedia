# university/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import University, Degree, Branch
from .serializers import UniversitySerializer, DegreeSerializer, BranchSerializer
from accounts.views import is_staff, jwt_auth




@jwt_auth
def university_list(request):
    universities = University.objects.all()
    return render(request, 'university/university_list.html', {'universities': universities})

@jwt_auth
@user_passes_test(is_staff)
def university_create(request):
    if request.method == 'POST':
        serializer = UniversitySerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'University created successfully.')
            return redirect('university:university_list')
        else:
            messages.error(request, 'Error creating university. Please check your details.')
            errors = serializer.errors
    else:
        serializer = UniversitySerializer()
        errors = {}
    return render(request, 'university/university_form.html', {
        'serializer': serializer,
        'errors': errors
    })

@jwt_auth
@user_passes_test(is_staff)
def university_update(request, pk):
    university = get_object_or_404(University, pk=pk)
    if request.method == 'POST':
        serializer = UniversitySerializer(university, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'University updated successfully.')
            return redirect('university:university_list')
        else:
            messages.error(request, 'Error updating university. Please check your details.')
            errors = serializer.errors
    else:
        serializer = UniversitySerializer(university)
        errors = {}
    return render(request, 'university/university_form.html', {
        'serializer': serializer,
        'errors': errors
    })

@jwt_auth
@user_passes_test(is_staff)
def university_delete(request, pk):
    university = get_object_or_404(University, pk=pk)
    university.delete()
    messages.success(request, 'University deleted successfully.')
    return redirect('university:university_list')

@jwt_auth
@user_passes_test(is_staff)
def degree_create(request):
    if request.method == 'POST':
        serializer = DegreeSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Degree created successfully.')
            return redirect('university:degree_list')
        else:
            messages.error(request, 'Error creating degree. Please check your details.')
            errors = serializer.errors
    else:
        serializer = DegreeSerializer()
        errors = {}
    return render(request, 'university/degree_form.html', {
        'serializer': serializer,
        'universities': University.objects.filter(is_active=True),
        'errors': errors
    })

@jwt_auth
def degree_list(request):
    degrees = Degree.objects.all()
    return render(request, 'university/degree_list.html', {'degrees': degrees})

@jwt_auth
@user_passes_test(is_staff)
def degree_delete(request, pk):
    degree = get_object_or_404(Degree, pk=pk)
    degree.delete()
    messages.success(request, 'Degree deleted successfully.')
    return redirect('university:degree_list')

@jwt_auth
@user_passes_test(is_staff)
def degree_update(request, pk):
    degree = get_object_or_404(Degree, pk=pk)
    if request.method == 'POST':
        serializer = DegreeSerializer(degree, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Degree updated successfully.')
            return redirect('university:degree_list')
        else:
            messages.error(request, 'Error updating degree. Please check your details.')
            errors = serializer.errors
    else:
        serializer = DegreeSerializer(degree)
        errors = {}
    return render(request, 'university/degree_form.html', {
        'serializer': serializer,
        'universities': University.objects.filter(is_active=True),
        'errors': errors
    })

@jwt_auth
@user_passes_test(is_staff)
def branch_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)

        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Branch created successfully.')
            return redirect('university:branch_list')
        else:
            messages.error(request, 'Error creating branch. Please check your details.')
            errors = serializer.errors
    else:
        serializer = BranchSerializer()
        errors = {}
    return render(request, 'university/branch_form.html', {
        'serializer': serializer,
        'degrees': Degree.objects.filter(is_active=True),
        'errors': errors
    })

@jwt_auth
def branch_list(request):
    branches = Branch.objects.all()
    return render(request, 'university/branch_list.html', {'branches': branches})

@jwt_auth
@user_passes_test(is_staff)
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    branch.delete()
    messages.success(request, 'Branch deleted successfully.')
    return redirect('university:branch_list')

@jwt_auth
@user_passes_test(is_staff)
def branch_update(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        serializer = BranchSerializer(branch, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Branch updated successfully.')
            return redirect('university:branch_list')
        else:
            messages.error(request, 'Error updating branch. Please check your details.')
            errors = serializer.errors
    else:
        serializer = BranchSerializer(branch)
        errors = {}
    return render(request, 'university/branch_form.html', {
        'serializer': serializer,
        'degrees': Degree.objects.filter(is_active=True),
        'errors': errors
    })
