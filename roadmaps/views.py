from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Roadmap, Syllabus
from .serializers import RoadmapSerializer, SyllabusSerializer
from accounts.views import is_staff, jwt_auth
# roadmaps/views.py


@jwt_auth
def syllabus_list(request):
    syllabi = Syllabus.objects.all()
    return render(request, 'roadmaps/syllabus_list.html', {'syllabi': syllabi})


@jwt_auth
@user_passes_test(is_staff)
def syllabus_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)
        serializer = SyllabusSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Syllabus created successfully.')
            return redirect('roadmaps:syllabus_list')
        else:
            messages.error(request, 'Error creating syllabus. Please check the errors below.')
            errors = serializer.errors
    else:
        serializer = SyllabusSerializer()
        errors = {}

    return render(request, 'roadmaps/syllabus_form.html', {
        'serializer': serializer,
        'errors': errors
    })


@jwt_auth
@user_passes_test(is_staff)
def syllabus_update(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)

    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)
        serializer = SyllabusSerializer(syllabus, data=data)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Syllabus updated successfully.')
            return redirect('roadmaps:syllabus_list')
        else:
            messages.error(request, 'Error updating syllabus.')
            errors = serializer.errors
    else:
        serializer = SyllabusSerializer(syllabus)
        errors = {}

    return render(request, 'roadmaps/syllabus_form.html', {
        'serializer': serializer,
        'errors': errors
    })


@jwt_auth
@user_passes_test(is_staff)
def syllabus_delete(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)
    syllabus.delete()
    messages.success(request, 'Syllabus deleted successfully.')
    return redirect('roadmaps:syllabus_list')


@jwt_auth
def roadmap_list(request):
    roadmaps = Roadmap.objects.all()
    return render(request, 'roadmaps/roadmap_list.html', {'roadmaps': roadmaps})


@jwt_auth
@user_passes_test(is_staff)
def roadmap_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)
        serializer = RoadmapSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Roadmap created successfully.')
            return redirect('roadmaps:roadmap_list')
        else:
            messages.error(request, 'Error creating roadmap.')
            errors = serializer.errors
    else:
        serializer = RoadmapSerializer()
        errors = {}

    return render(request, 'roadmaps/roadmap_form.html', {
        'serializer': serializer,
        'errors': errors
    })


@jwt_auth
@user_passes_test(is_staff)
def roadmap_update(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)

    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)
        serializer = RoadmapSerializer(roadmap, data=data)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Roadmap updated successfully.')
            return redirect('roadmaps:roadmap_list')
        else:
            messages.error(request, 'Error updating roadmap.')
            errors = serializer.errors
    else:
        serializer = RoadmapSerializer(roadmap)
        errors = {}

    return render(request, 'roadmaps/roadmap_form.html', {
        'serializer': serializer,
        'errors': errors
    })


@jwt_auth
@user_passes_test(is_staff)
def roadmap_delete(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)
    roadmap.delete()
    messages.success(request, 'Roadmap deleted successfully.')
    return redirect('roadmaps:roadmap_list')
