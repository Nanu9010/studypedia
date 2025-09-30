# notes/models.py
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from university.models import Branch
from ecommerce.utils import default_pdf

class Note(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    credit_price = models.PositiveIntegerField(default=0)
    code = models.CharField(max_length=20, unique=True, blank=True)  # New field for auto-incrementing code
    pdf_file = models.FileField(
        upload_to='notes/files/',default=default_pdf,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip']
        )],null=False,blank=False
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.code:
            with transaction.atomic():
                last_note = Note.objects.order_by('-id').first()
                if last_note and last_note.code.startswith('NOTE'):
                    try:
                        last_number = int(last_note.code.replace('NOTE', ''))
                        new_number = last_number + 1
                    except ValueError:
                        new_number = 1
                else:
                    new_number = 1
                self.code = f'NOTE{new_number:03d}'  # e.g., NOTE001, NOTE002
                while Note.objects.filter(code=self.code).exists():
                    new_number += 1
                    self.code = f'NOTE{new_number:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.code}"