from django.urls import path
from .views import (CompanyCreateView, CompanyDetailView,
                    StorageView, StorageDetailView,
                    SupplierListView, SupplyCreateView,
                    ProductListView, ProductDetailView,
                    SupplyListView, SupplierDetailView,
                    AddEmployeeView, SaleListView,
                    SaleCreateView, SaleDetailView,
                    SalesAnalyticsView, SupplyInvoiceView,
                    SalesChartsView)


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

    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sales/create/', SaleCreateView.as_view(), name='sale-create'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),

    path('analytics/sales/', SalesAnalyticsView.as_view(), name='sales-analytics'),
    path('analytics/charts/', SalesChartsView.as_view(), name='sales-charts'),
    path('supplies/<int:pk>/invoice/', SupplyInvoiceView.as_view(), name='supply-invoice'),

]