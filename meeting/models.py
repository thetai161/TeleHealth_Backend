from django.db import models
from authentication.models import User
import uuid

# Create your models here.


class Meeting(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting_title = models.CharField(max_length=200)
    meeting_time_start = models.DateTimeField()
    meeting_time_end = models.DateTimeField()
    meeting_content = models.CharField(max_length=200)
    calendar_id = models.CharField(max_length=200)
    calendar_url = models.CharField(max_length=200)
    meeting_url = models.CharField(max_length=200)
    conclusion = models.TextField(null=True)
    url_file = models.CharField(max_length=200, default='')
    is_valid = models.BooleanField(default=True)

    meeting_creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='meeting')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meeting"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.meeting_title)


class MeetingGuest(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name='meeting_guest')
    meeting_guest = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='meeting_guest')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "meeting_guest"
        ordering = ["created_at"]

    def __str__(self):
        return '{}'.format(self.id)
