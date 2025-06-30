from django.contrib import admin
from .models import Company, Storage, Supplier, Product, Supply, SupplyProduct

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'INN', 'created_at', 'updated_at')
    search_fields = ('title', 'INN')


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('company', 'address')
    list_filter = ('company',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'contact_person', 'phone')
    list_filter = ('company',)
    search_fields = ('name', 'contact_person', 'phone')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'storage', 'quantity', 'purchase_price', 'selling_price')
    list_filter = ('storage__company', 'storage')
    search_fields = ('title', 'description')


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'storage', 'created_at')
    list_filter = ('storage__company', 'supplier')
    date_hierarchy = 'created_at'


@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('supply', 'product', 'quantity', 'purchase_price')
    list_filter = ('supply__storage__company',)


