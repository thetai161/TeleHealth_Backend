from .models import MeetingGuest, Meeting
from rest_framework import serializers
from authentication.models import User


class MeetingSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            meetingGuest = MeetingGuest.objects.filter(meeting_id=instance.id)
            meetingGuestData = MeetingGuestSerializer(
                meetingGuest, many=True).data
        except:
            meetingGuestData = ''
        representation['meeting_guest'] = meetingGuestData

        return representation

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['meeting_time_start', 'meeting_time_end', 'meeting_content', 'meeting_title']


class MeetingReadOnlySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            meetingGuest = MeetingGuest.objects.filter(meeting_id=instance.id)
            meetingGuestData = MeetingGuestSerializer(
                meetingGuest, many=True).data
        except:
            meetingGuestData = ''
        try:
            user = User.objects.get(id=instance.meeting_creator.id)
            creatorEmail = user.email
            creatorPhone = user.phone
        except:
            creatorEmail = ''
            creatorPhone = ''
        representation['creatorEmail'] = creatorEmail
        representation['creatorPhone'] = creatorPhone
        representation['meetingGuest'] = meetingGuestData

        return representation

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingGuestSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            meetingGuest = User.objects.get(meeting_guest__id=instance.id)
            meetingGuestData = meetingGuest.email
        except:
            meetingGuestData = ''
        representation['meeting_guest_email'] = meetingGuestData

        return representation

    class Meta:
        model = MeetingGuest
        fields = '__all__'


class MeetingReadOnlyCreatorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            meetingGuest = MeetingGuest.objects.filter(meeting_id=instance.id)
            meetingGuestData = MeetingGuestSerializer(
                meetingGuest, many=True).data
        except:
            meetingGuestData = ''
        representation['meeting_guest'] = meetingGuestData

        return representation

    class Meta:
        model = Meeting
        fields = '__all__'
