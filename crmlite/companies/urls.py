from django.urls import path
from .views import (CompanyCreateView, CompanyDetailView,
                    StorageView, StorageDetailView,
                    SupplierListView, SupplyCreateView,
                    ProductListView, ProductDetailView,
                    SupplyListView, SupplierDetailView,
                    AddEmployeeView)


urlpatterns = [
    path('', CompanyCreateView.as_view(), name='company-create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
    path('storages/', StorageView.as_view(), name='storages-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),

    path('suppliers/', SupplierListView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),

    path('products/', ProductListView.as_view(), name='products-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='products-detail'),

    path('supplies/', SupplyListView.as_view(), name='supply-list'),
    path('supplies/create/', SupplyCreateView.as_view(), name='supply-create'),

    path('add-employee/', AddEmployeeView.as_view(), name='add-employee'),
]