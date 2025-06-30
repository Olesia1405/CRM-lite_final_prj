from rest_framework import permissions
from .models import Company, Storage


class IsCompanyEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.company is not None


class IsCompanyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_company_owner

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Company):
            return request.user.is_company_owner and request.user.company == obj
        elif isinstance(obj, Storage):
            return request.user.is_company_owner and request.user.company == obj.company
        return False