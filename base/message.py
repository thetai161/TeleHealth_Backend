from rest_framework.response import Response
from rest_framework import status


def error(message='', data={}):

    return Response({"error": False, "message": message, "data": data}, status=status.HTTP_400_BAD_REQUEST)


def success(message='', data={}):

    return Response({"success": True, "message": message, "data": data}, status=status.HTTP_200_OK)
