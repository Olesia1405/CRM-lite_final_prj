from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Company, Storage
from .serializers import CompanySerializer, StorageSerializer
from users.models import User


class CompanyCreateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        company = serializer.save()
        user = self.request.user
        user.is_company_owner = True
        user.company = company
        user.save()


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsCompanyOwner()]

    def get_queryset(self):
        user = self.request.user
        return Company.objects.filter(employees=user)


class StorageView(generics.ListCreateAPIView):
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.company:
            return Storage.objects.none()
        return Storage.objects.filter(company=user.company)

    def perform_create(self, serializer):
        if not self.request.user.is_company_owner:
            raise permissions.PermissionDenied("Only company owner can create storages")
        serializer.save(company=self.request.user.company)


class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsCompanyOwner()]

    def get_queryset(self):
        user = self.request.user
        if not user.company:
            return Storage.objects.none()
        return Storage.objects.filter(company=user.company)


class IsCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Company):
            return request.user.is_company_owner and request.user.company == obj
        elif isinstance(obj, Storage):
            return request.user.is_company_owner and request.user.company == obj.company
        return False