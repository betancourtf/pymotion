import base64
from uuid import uuid4

from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import MoodCapture


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        print("In to internal native")
        if isinstance(data, str) and data.startswith('data:image'):
            print("Decoding image")
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension
            try:
                data = ContentFile(base64.b64decode(imgstr), name='{}.{}'.format(uuid4(),ext))
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError("There was an error with the image file")
        return super(Base64ImageField, self).to_internal_value(data)



class MoodCapturePostSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=100, allow_empty_file=False)
    class Meta:
        model = MoodCapture
        fields = ('user','latitude', 'longitude', 'image')
        
        
class MoodCaptureListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodCapture
        fields = ('latitude', 'longitude', 'mood', 'created_at')


class CloseByHappyPlaceListSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField()
    class Meta:
        model = MoodCapture
        fields = ('latitude', 'longitude', 'distance', 'created_at')
        

class ClosestHappyPlaceSerializer(serializers.Serializer):
    # Current location of user
    latitude = serializers.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = serializers.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    # Offsets to use for search
    lat_offset = serializers.FloatField(validators=[MinValueValidator(0.000001), MaxValueValidator(0.4)],default=0.02)
    lon_offset = serializers.FloatField(validators=[MinValueValidator(0.000001), MaxValueValidator(0.4)],default=0.02)