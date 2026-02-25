from rest_framework import serializers
from .models import University, Degree, Branch

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'abbreviation', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DegreeSerializer(serializers.ModelSerializer):
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.filter(is_active=True))
    class Meta:
        model = Degree
        fields = ['id', 'university', 'name', 'abbreviation', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BranchSerializer(serializers.ModelSerializer):
    degree = serializers.PrimaryKeyRelatedField(queryset=Degree.objects.filter(is_active=True))

    class Meta:
        model = Branch
        fields = ['id', 'degree', 'name', 'abbreviation', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

