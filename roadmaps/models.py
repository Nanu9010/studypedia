from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from ecommerce.utils import default_pdf
# roadmaps/models.py

class Syllabus(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, blank=True)
    pdf_file = models.FileField(
        upload_to='roadmaps/syllabus/',
        default=default_pdf,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip']
        )],
        null=False,
        blank=False
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.code:
            with transaction.atomic():
                last_syllabus = Syllabus.objects.order_by('-id').first()
                if last_syllabus and last_syllabus.code.startswith('SYLLABUS'):
                    try:
                        last_number = int(last_syllabus.code.replace('SYLLABUS', ''))
                        new_number = last_number + 1
                    except ValueError:
                        new_number = 1
                else:
                    new_number = 1
                self.code = f'SYLLABUS{new_number:03d}'
                while Syllabus.objects.filter(code=self.code).exists():
                    new_number += 1
                    self.code = f'SYLLABUS{new_number:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.code}"


class Roadmap(models.Model):
    name = models.CharField(max_length=255)
    pdf_file = models.FileField(
        upload_to='roadmaps/roadmap/',
        default=default_pdf,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip']
        )],
        null=False,
        blank=False
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
