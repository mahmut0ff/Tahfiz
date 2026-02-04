from rest_framework import views
from apps.student.models import Student
from apps.group.models import Group
from rest_framework.response import Response
from .serializers import *
from django.db.models import Q
from rest_framework.views import APIView
from datetime import datetime
from apps.schedule.models import Subject
from apps.grade.models import Grade
from rest_framework.permissions import IsAuthenticated

class StudentRetrieveView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        "Получение студента. Требуется токен"
        student = Student.objects.get(user__id=request.user.id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)


class GroupListView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        "Получение списка групп студента. Требуется токен"
        student = Student.objects.get(user__id=request.user.id)
        groups = Group.objects.filter(student=student).order_by('-id')
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class GroupRetrieveView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        "Получение группы студента. Требуется токен и id группы"
        group = Group.objects.get(id=pk)
        serializer = GroupSerializer(group)
        return Response(serializer.data)
    

class DiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        "Получение дневника студента. Требуется токен"
        student = Student.objects.get(user__id=request.user.id)
        subjects = Subject.objects.order_by('name')
        grades = Grade.objects.filter(student=student).order_by('date')
        date = request.GET.get('month')
        
        if date:
            year, month = date.split('-')
            grades = grades.filter(Q(date__month=month) & Q(date__year=year))
        else:
            date = f'{datetime.now().year}-{datetime.now().month:02}'
        
        days = grades.dates('date', 'day')
        
        return Response({
            'student': student.id,
            'subjects': [subject.name for subject in subjects],
            'grades': GradeSerializer(grades, many=True).data,
            'days': [day.strftime('%Y-%m-%d') for day in days],
            'date': date
        })
    
