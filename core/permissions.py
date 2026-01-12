# core/permissions.py
from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """ Allows access only to Super Admins """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'

class IsInstituteAdmin(permissions.BasePermission):
    """ Allows access only to Institute Admins """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'INSTITUTE_ADMIN'

class IsTeacher(permissions.BasePermission):
    """ Allows access to Teachers """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TEACHER'