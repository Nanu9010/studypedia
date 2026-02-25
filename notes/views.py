# notes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Note
from .serializers import NoteSerializer
from university.models import Branch
from accounts.views import is_staff, jwt_auth

@jwt_auth
def note_list(request):
    notes = Note.objects.filter(is_active=True)
    return render(request, 'notes/note_list.html', {'notes': notes})

@jwt_auth
@user_passes_test(is_staff)
def note_create(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)  # merge files into POST
        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Note created successfully.')
            return redirect('notes:note_list')
        else:
            messages.error(request, 'Error creating note.')
            errors = serializer.errors
    else:
        serializer = NoteSerializer()
        errors = {}

    return render(request, 'notes/note_form.html', {
        'serializer': serializer,
        'errors': errors
    })


@jwt_auth
@user_passes_test(is_staff)
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.FILES)  # merge files into POST
        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Note updated successfully.')
            return redirect('notes:note_list')
        else:
            messages.error(request, 'Error updating note.')
            errors = serializer.errors
    else:
        serializer = NoteSerializer()
        errors = {}

    return render(request, 'notes/note_form.html', {
        'serializer': serializer,
        'errors': errors
    })



@jwt_auth
@user_passes_test(is_staff)
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    messages.success(request, 'Note deleted successfully.')
    return redirect('notes:note_list')