import requests

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core import validators
from django.contrib.auth.models import User

class MoodCapture(models.Model):
    # We could also create a mood table but let's keep it simple
    # Asuming we'll use Microsoft Emotion API so we use the same emotions as they use
    MOODS_CHOICES = (
        ('AN', 'Anger'),
        ('CO','Contempt'),
        ('DI','Disgust'),
        ('FE','Fear'),
        ('HA','Happiness'),
        ('NE','Neutral'),
        ('SA','Sadness'),
        ('SU', 'Surprise'),
    )
    EMOTION_MOOD_DICT = {
        'anger': 'AN',
        'contempt': 'CO',
        'disgust': 'DI',
        'fear': 'FE',
        'happiness': 'HA',
        'neutral': 'NE',
        'sadness': 'SA',
        'surprise': 'SU',
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField(validators=[validators.MinValueValidator(-90), validators.MaxValueValidator(90)])
    longitude = models.FloatField(validators=[validators.MinValueValidator(-180), validators.MaxValueValidator(180)])
    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', default='')
    is_recognized = models.BooleanField(default=False)
    # Another option would be to store all the posible moods, for simplicity let's store the highest ranked
    mood = models.CharField(max_length=2, choices= MOODS_CHOICES, default="")
    # Image goes here
    created_at = models.DateTimeField(default=timezone.now)
    
    
    def recognize(self):
        image_path = self.image.path
        image_data = open(image_path, "rb").read()
        headers  = {'Ocp-Apim-Subscription-Key': settings.EMOTIONS_API_KEY, "Content-Type": "application/octet-stream" }
        # All this attributes work
        # 'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
        params = {'returnFaceId': 'true', 'returnFaceLandmarks': 'false', 'returnFaceAttributes':'emotion'}
        try:
            response = requests.post(settings.EMOTIONS_API_RECOGNIZE_URL, params=params, headers=headers, data=image_data)
        except:
            print("An error ocurred while consuming Emotions API")
            return
        analysis = response.json()
        return analysis

    @staticmethod
    def get_mood_from_analysis(analysis):
        if len(analysis)!=1:
            print("Error processing image. Image should only have one face")
            return ""
        # Get the dominant mood from the image
        dominant_mood_score=0
        dominant_mood=""
        for mood,score in analysis[0]['faceAttributes']['emotion'].items():
            if score > dominant_mood_score:
                dominant_mood_score = score
                dominant_mood = mood
        return MoodCapture.EMOTION_MOOD_DICT[dominant_mood]
        
    def recognize_and_save(self):
        analysis = self.recognize()
        self.mood = MoodCapture.get_mood_from_analysis(analysis)
        if self.mood:
            self.is_recognized=True
        print("Saving as {} image".format(self.mood))
        self.save()
    
    def save(self, *args, **kwargs):
        # Only when creating and object recognize it
        if not self.pk:
            # Save image to disk before doing recognition
            super(MoodCapture, self).save(*args, **kwargs)
            # No do recognition, ideally we should do this in a queue like Celery
            self.mood=MoodCapture.get_mood_from_analysis(self.recognize())
            if self.mood:
                self.is_recognized = True
            self.save()
            return
        super(MoodCapture, self).save(*args, **kwargs)
        
    


    
    
        
    
    

#class MoodFrequency(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    mood = models.CharField(max_length=2, choices = MoodCapture.MOODS_CHOICES)
#    frequency = models.BigIntegerField(default=1)

