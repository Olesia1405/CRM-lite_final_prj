from django.urls import path
from .views import CompanyCreateView, CompanyDetailView, StorageView, StorageDetailView


urlpatterns = [
    path('', CompanyCreateView.as_view(), name='company-create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('storages/', StorageView.as_view(), name='storages-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
]