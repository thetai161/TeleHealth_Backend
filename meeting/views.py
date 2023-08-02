from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from pprint import pprint
from .Google import create_service, convert_to_RFC_datetime

from authentication.mixins import GetSerializerClassMixin
from upload.serializers import FileSerializer
from .models import Meeting, MeetingGuest
from .serializers import MeetingGuestSerializer, MeetingSerializer, MeetingReadOnlySerializer, MeetingUpdateSerializer, MeetingReadOnlyCreatorSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from authentication.permissions import Role1, Role1or3, Role2, Role3, Role4
from notification.models import Notification


class MeetingViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    serializer_action_classes = {
        'create': MeetingReadOnlySerializer,
        'update': MeetingUpdateSerializer,
    }
    permission_classes_by_action = {
        'list': [Role3],
        "create": [Role1],
        "update": [Role1],
        "listMeetingMissingConclusion": [Role1, Role3],
        # "listMeetingCreatorForUser": [Role1, Role3],
        # "addMeetingConclusion": [Role1],

    }

    def create(self, request, *args, **kwargs):
        try:
            meetingData = request.data
            userId = request.user.id
            userObject = User.objects.get(id=userId)

            CLIENT_SECRET_FILE = './meeting/client_secret.json'
            API_NAME = 'calendar'
            API_VERSION = 'v3'
            SCOPES = ['https://www.googleapis.com/auth/calendar']

            service = create_service(
                CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

            calendar_id = 'telehealth.ibmelab@gmail.com'
            house_adjustment = -8
            start = meetingData['meeting_time_start']
            end = meetingData['meeting_time_end']
            even_request_body = {
                "start": {
                    "dateTime": convert_to_RFC_datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13])+house_adjustment, int(start[14:16])),
                    "timeZone": 'Asia/Ho_Chi_Minh'
                },
                "end": {
                    "dateTime": convert_to_RFC_datetime(int(end[0:4]), int(end[5:7]), int(end[8:10]), int(end[11:13])+house_adjustment, int(end[14:16])),
                    "timeZone": 'Asia/Ho_Chi_Minh'
                },
                "conferenceData": {
                    "createRequest": {
                        "conferenceSolutionKey": {
                            "type": "hangoutsMeet"
                        },
                        "requestId": "RandomString"
                    }
                },
                "summary": meetingData['meeting_title'],
                "description": meetingData['meeting_content'],
                "colorId": 5,
                "status": 'confirmed',
                "attachments": meetingData['url_file'],
                "attendees": meetingData['meeting_guest']
            }
            maxAttendees = 20
            sendNotification = True
            supportsAttachments = True
            response = service.events().insert(
                calendarId=calendar_id,
                maxAttendees=maxAttendees,
                sendNotifications=sendNotification,
                supportsAttachments=supportsAttachments,
                body=even_request_body,
                conferenceDataVersion=1,
            ).execute()
            pprint(response)
            meeting = Meeting.objects.create(
                meeting_title=meetingData['meeting_title'],
                meeting_time_start=meetingData['meeting_time_start'],
                meeting_time_end=meetingData['meeting_time_end'],
                meeting_content=meetingData['meeting_content'],
                meeting_url=response['hangoutLink'],
                calendar_url=response['htmlLink'],
                calendar_id=response['id'],
                url_file=meetingData['url_file'][0]['fileUrl'],
                meeting_creator_id=userId,
            )
            for meetingGuest in meetingData['meeting_guest']:
                guest = User.objects.filter(email=meetingGuest['email'])
                if len(guest)==1:
                    meetingGuestOJ = MeetingGuest.objects.create(
                        meeting=meeting,
                        meeting_guest=guest[0],
                    )
                    notification = Notification.objects.create(
                        user=guest[0],
                        content=f"You have a meeting invitation from {userObject.email}",
                        linkId=meeting.id
                    )
            meetingSerializer = self.get_serializer(meeting)
            return success(data=meetingSerializer.data)
        except Exception as err:
            print("=======", err)
            return error(data="Not valid data")

    def update(self, request, *args, **kwargs):
        try:
            emailUser = request.user.email
            meetingId = self.request.GET.get('pk')
            meetingData = request.data
            meeting = Meeting.objects.get(id=meetingId)
            meetingSerializer = self.get_serializer(
                instance=meeting, data=meetingData)
            meetingSerializer.is_valid(raise_exception=True)
            self.perform_update(meetingSerializer)
            MeetingGuest.objects.filter(meeting_id=meetingId).delete()
            meetingGuests = meetingData['guest']
            if meetingGuests != 'null':
                for meetingGuest in meetingGuests:
                    guest = User.objects.filter(email=meetingGuest['email'])
                    if len(guest)==1:
                        meetingGuestOJ = MeetingGuest.objects.create(
                            meeting=meeting,
                            meeting_guest=guest[0],
                        )
                        notification = Notification.objects.create(
                            user=guest[0],
                            content=f"You have a meetings update from {emailUser}",
                            linkId=meeting.id
                        )
            start = meetingData['meeting_time_start']
            end = meetingData['meeting_time_end']
            house_adjustment = -8
            even_request_body = {
                "start": {
                    "dateTime": convert_to_RFC_datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13])+house_adjustment, int(start[14:16])),
                    "timeZone": 'Asia/Ho_Chi_Minh'
                },
                "end": {
                    "dateTime": convert_to_RFC_datetime(int(end[0:4]), int(end[5:7]), int(end[8:10]), int(end[11:13])+house_adjustment, int(end[14:16])),
                    "timeZone": 'Asia/Ho_Chi_Minh'
                },
                "description": meetingData['meeting_content'],
                "attendees": meetingData['guest'],
            }
            CLIENT_SECRET_FILE = './meeting/client_secret.json'
            API_NAME = 'calendar'
            API_VERSION = 'v3'
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            service = create_service(
                CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
            request = service.events().update(
                calendarId='telehealth.ibmelab@gmail.com',
                eventId=meeting.calendar_id,
                body=even_request_body,
            ).execute()
            pprint(request)
            dataCalendarSerializer = MeetingReadOnlySerializer(meeting)
            return success(data=dataCalendarSerializer.data)
        except:
            return error('data not valid')

    def read(self, request, *args, **kwargs):
        meetingId = self.request.GET.get('pk')
        meeting = Meeting.objects.get(id=meetingId)
        meetingSerializer = MeetingReadOnlySerializer(instance=meeting)
        return success(data=meetingSerializer.data)

    def addMeetingConclusion(self, request, *args, **kwargs):
        meetingId = self.request.GET.get('pk')
        meeting = Meeting.objects.get(id=meetingId)
        meeting.conclusion = request.data['conclusion']
        meeting.save()
        meetingSerializer = MeetingSerializer(instance=meeting)
        return success(data=meetingSerializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list_meeting_missing_conclusion"
    )
    def listMeetingMissingConclusion(self, request, *args, **kwargs):
        userId = request.user.id
        meetings = Meeting.objects.filter(
            meeting_creator_id=userId, conclusion=None)
        meetingSerializer = MeetingSerializer(meetings, many=True)
        return success(data=meetingSerializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list_meeting_creator_for_user"
    )
    def listMeetingCreatorForUser(self, request, *args, **kwargs):
        userId = request.user.id
        meetings = Meeting.objects.filter(meeting_creator_id=userId)
        meetingSerializer = MeetingReadOnlyCreatorSerializer(meetings, many=True)
        return success(data=meetingSerializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list_meeting_valid_for_user"
    )
    def listMeetingValidForUser(self, request, *args, **kwargs):
        userId = request.user.id
        meetings = Meeting.objects.filter(
            meeting_guest__meeting_guest_id=userId)
        meetingSerializer = MeetingSerializer(meetings, many=True)
        return success(data=meetingSerializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list_meeting_for_user"
    )
    def listMeetingForUser(self, request, *args, **kwargs):
        userId = request.user.id
        meetings = Meeting.objects.filter(
            meeting_guest__meeting_guest_id=userId)
        meetingSerializer = MeetingSerializer(meetings, many=True)
        return success(data=meetingSerializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="end_edit_conclusion"
    )
    def endEditConclusion(self, request, *args, **kwargs):
        meetingId = self.request.GET.get('pk')
        meeting = Meeting.objects.get(id=meetingId)
        meeting.is_valid = False
        meeting.save()
        return success(data="ok")