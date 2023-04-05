from rest_framework import permissions
from doctor.models import Doctor


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class Role2(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user.role == 'role2':
            return bool(request.user and request.user.role)


class Role1(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user.role == 'role1':
            return bool(request.user and request.user.role)


class Role3(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user.role == 'role3':
            return True


class Role4(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user.role == 'role4':
            return bool(request.user and request.user.role)


class Role1or3(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.user.role == 'role1' and Doctor.objects.get(user_id=request.user.id).is_accept == True:
            role = True
        else:
            role = False
        if request.user.role == 'role3' or role:
            return bool(request.user and request.user.role)
