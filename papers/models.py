# papers/models.py
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from university.models import Branch  # Updated import
from ecommerce.utils import default_pdf


class Paper(models.Model):
    EXAM_TYPE_CHOICES = [
        ('insem', 'In-Semester'),
        ('endsem', 'End-Semester'),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='papers')  # Changed from subject to branch
    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    year = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    credit_price = models.PositiveIntegerField(default=0)
    code = models.CharField(max_length=20, unique=True, blank=True)
    pdf_file = models.FileField(
        upload_to='papers/files/', default=default_pdf,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip']
        )],null=False,blank=False
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'year', 'exam_type']  # Updated ordering to include name

    def save(self, *args, **kwargs):
        if not self.code:
            with transaction.atomic():
                last_paper = Paper.objects.order_by('-id').first()
                if last_paper and last_paper.code.startswith('PAPER'):
                    try:
                        last_number = int(last_paper.code.replace('PAPER', ''))
                        new_number = last_number + 1
                    except ValueError:
                        new_number = 1
                else:
                    new_number = 1
                self.code = f'PAPER{new_number:03d}'
                while Paper.objects.filter(code=self.code).exists():
                    new_number += 1
                    self.code = f'PAPER{new_number:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_exam_type_display()} ({self.year}) - {self.code}"