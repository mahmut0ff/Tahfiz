from rest_framework import serializers
from apps.student.models import Student
from apps.group.models import Group
from apps.grade.models import Grade


class StudentSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(many=True)
    class Meta:
        model = Student
        fields = '__all__'
    

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'mark', 'pages', 'subject', 'teacher', 'date']

