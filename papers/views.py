# papers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Paper
from .serializers import PaperSerializer
from university.models import Branch  # Updated import
from accounts.views import is_staff, jwt_auth

@jwt_auth
def paper_list(request):
    papers = Paper.objects.filter(is_active=True)
    return render(request, 'papers/paper_list.html', {'papers': papers})

@jwt_auth
@user_passes_test(is_staff)
def paper_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)
        serializer = PaperSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Paper created successfully.')
            return redirect('papers:paper_list')
        else:
            messages.error(request, 'Error creating paper. Please check the errors below.')
            errors = serializer.errors
            print("Serializer errors:", errors)  # Debugging
    else:
        serializer = PaperSerializer()
        errors = {}
    return render(request, 'papers/paper_form.html', {
        'serializer': serializer,
        'branches': Branch.objects.filter(is_active=True),  # Changed to branches
        'errors': errors
    })

@jwt_auth
@user_passes_test(is_staff)
def paper_update(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    if request.method == 'POST':
        data = request.POST.copy()
        if request.FILES:
            data.update(request.FILES)
        serializer = PaperSerializer(paper, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Paper updated successfully.')
            return redirect('papers:paper_list')
        else:
            messages.error(request, 'Error updating paper. Please check the errors below.')
            errors = serializer.errors
            print("Serializer errors:", errors)  # Debugging
    else:
        serializer = PaperSerializer(paper)
        errors = {}
    return render(request, 'papers/paper_form.html', {
        'serializer': serializer,
        'branches': Branch.objects.filter(is_active=True),  # Changed to branches
        'errors': errors
    })

@jwt_auth
@user_passes_test(is_staff)
def paper_delete(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    paper.delete()
    messages.success(request, 'Paper deleted successfully.')
    return redirect('papers:paper_list')