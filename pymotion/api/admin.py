from django.contrib import admin

from .models import MoodCapture

class MoodCaptureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'latitude', 'longitude', 'mood', 'created_at', 'is_recognized')

admin.site.register(MoodCapture, MoodCaptureAdmin)
