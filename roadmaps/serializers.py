from rest_framework import serializers
from .models import Roadmap, Syllabus
# roadmaps/serializers.py

class RoadmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadmap
        fields = [
            'id', 'name', 'pdf_file', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = [
            'id', 'name', 'code',
            'pdf_file', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def validate_pdf_file(self, value):
        if value:
            max_size = 10 * 1024 * 1024  # 10 MB
            if value.size > max_size:
                raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value
