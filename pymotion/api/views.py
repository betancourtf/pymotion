from django.utils.timezone import now, timedelta

from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#from django.shortcuts import render

from .models import MoodCapture
from .serializers import MoodCapturePostSerializer, MoodCaptureListSerializer

class UserMood(ViewSet):
    
    def create(self, request):
        if request.token_user:
            request.data['user']=request.token_user.id
        serializer = MoodCapturePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request):
        if request.token_user:
            queryset = MoodCapture.objects.filter(user=request.token_user,created_at__gte=now()-timedelta(days=30)).order_by('-created_at')
            serializer = MoodCaptureListSerializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'detail':'User Token Error - There was an error while validating your user'}, status=status.HTTP_400_BAD_REQUEST)


class UserMoodHistrogram(ViewSet):
    def list(self,request):
        if request.token_user:
            histogram = {}
            for choice,mood_string in MoodCapture.MOODS_CHOICES:
                histogram[mood_string] = MoodCapture.objects.filter(user=request.token_user,
                                                                    created_at__gte=now()-timedelta(days=30),
                                                                    mood = choice
                                                                    ).count()
            return Response(histogram)
        return Response({'detail':'User Token Error - There was an error while validating your user'}, status=status.HTTP_400_BAD_REQUEST)