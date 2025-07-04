import django_filters
from .models import Sale


class SaleFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='sale_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sale_date', lookup_expr='lte')

    class Meta:
        model = Sale
        fields = ['start_date', 'end_date']