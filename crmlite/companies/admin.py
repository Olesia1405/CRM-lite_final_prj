from django.contrib import admin
from .models import Company, Storage, Supplier, Product, Supply, SupplyProduct, Sale, ProductSale

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


class ProductSaleInLine(admin.TabularInline):
    model = ProductSale
    extra = 0
    readonly_fields = ('price', 'created_at')
    fields = ('product', 'quantity', 'price', 'created_at')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'total_amount', 'created_at')
    list_filter = ('company', 'created_at')
    search_fields = ('buyer_name',)
    inlines = [ProductSaleInLine]
    readonly_fields = ('total_amount', 'created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('company', 'created_by').prefetch_related('product_sales__product')