from geopy import distance

from django.utils.timezone import now, timedelta

from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import MoodCapture
from .serializers import ( MoodCapturePostSerializer, MoodCaptureListSerializer,
    ClosestHappyPlaceSerializer, CloseByHappyPlaceListSerializer)

class UserMood(ViewSet):
    
    def create(self, request):
        request.data['user']=request.token_user.id
        serializer = MoodCapturePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        queryset = MoodCapture.objects.filter(user=request.token_user, is_recognized=True,
                                              created_at__gte=now()-timedelta(days=30)).order_by('-created_at')
        serializer = MoodCaptureListSerializer(queryset, many=True)
        return Response(serializer.data)

    
class UserMoodHistrogram(ViewSet):
    def list(self,request):
        histogram = {}
        for choice,mood_string in MoodCapture.MOODS_CHOICES:
            histogram[mood_string] = MoodCapture.objects.filter(user=request.token_user,
                                                                is_recognized=True,
                                                                created_at__gte=now()-timedelta(days=30),
                                                                mood = choice
                                                                ).count()
        return Response(histogram)


class CloseByHappyPlace(ViewSet):
    def list(self,request):
        print(request.query_params)
        serializer = ClosestHappyPlaceSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_lat = serializer.validated_data.get('latitude')
        user_lon = serializer.validated_data.get('longitude')
        lat_offset = serializer.validated_data.get('lat_offset')
        lon_offset = serializer.validated_data.get('lon_offset')
        
        lat_low = user_lat - lat_offset
        lat_high = user_lat + lat_offset
        lon_low = user_lon - lon_offset
        lon_high = user_lon + lon_offset
        
        print("({},{})-({},{})".format(lat_low,lon_low,lat_high,lon_high))
        
        if lat_low < -90 or lat_high > 90 or lon_low < -180 or lon_high > 180:
            return Response({'details':'The user coordinates and the offset result in out of bound values'},
                            status=status.HTTP_400_BAD_REQUEST)
        close_by_happy_places = MoodCapture.objects.filter(latitude__gte=lat_low, latitude__lte=lat_high,
                                                           longitude__gte=lon_low, longitude__lte=lon_high,
                                                           user=request.token_user, created_at__gte=now()-timedelta(days=30),
                                                           is_recognized=True,mood="HA").order_by('-created_at')
        # Add the distance to the result
        for capture in close_by_happy_places:
            capture.distance = distance.distance((user_lat,user_lon),(capture.latitude,capture.longitude)).km
        response_serializer = CloseByHappyPlaceListSerializer(close_by_happy_places, many=True)
        return Response(response_serializer.data)
        
        