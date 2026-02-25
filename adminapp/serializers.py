# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from notes.models import PaperNote
# from roadmaps.models import Roadmap, Syllabus
# from university.models import University, Degree, Branch, Pattern, Subject
# from ecommerce.models import Coupon, Order
#
# User = get_user_model()
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'
#
# class PaperNoteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaperNote
#         fields = '__all__'
#
# class RoadmapSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Roadmap
#         fields = '__all__'
#
# class UniversitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = University
#         fields = '__all__'
#
# class DegreeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Degree
#         fields = '__all__'
#
# class BranchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Branch
#         fields = '__all__'
#
# class PatternSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pattern
#         fields = '__all__'
#
# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = '__all__'
#
# class SyllabusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Syllabus
#         fields = '__all__'
#
# class CouponSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Coupon
#         fields = '__all__'
#
# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'
