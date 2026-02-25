from django.db import models
from django.core.validators import FileExtensionValidator

class University(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Degree(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='degrees')
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Branch(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10 , null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


