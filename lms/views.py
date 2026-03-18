from django.shortcuts import render
from rest_framework import generics, viewsets

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer

# Create your views here.


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
