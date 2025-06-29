from django.contrib import admin
from .models import Company, Storage

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'INN', 'created_at', 'updated_at')
    search_fields = ('title', 'INN')


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('company', 'address')
    list_filter = ('company',)

