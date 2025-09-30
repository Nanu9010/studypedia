# papers/serializers.py
from rest_framework import serializers
from .models import Paper
from university.models import University, Degree, Branch

class PaperSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.filter(is_active=True)
    )
    university = serializers.CharField(source='branch.degree.university.name', read_only=True)
    degree = serializers.CharField(source='branch.degree.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    pdf_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Paper
        fields = [
            'id',
            'university',
            'degree',
            'branch',
            'branch_name',
            'name',  # Replaced subject_name
            'exam_type',
            'year',
            'price',
            'credit_price',
            'code',
            'pdf_file',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'university', 'degree', 'branch_name', 'code', 'created_at', 'updated_at']

    def validate_pdf_file(self, value):
        if value:
            max_size = 10 * 1024 * 1024  # 10 MB
            if value.size > max_size:
                raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value

    def validate(self, data):
        exam_type = data.get('exam_type')
        if exam_type and exam_type not in dict(Paper.EXAM_TYPE_CHOICES).keys():
            raise serializers.ValidationError({"exam_type": "Invalid exam type."})
        return data