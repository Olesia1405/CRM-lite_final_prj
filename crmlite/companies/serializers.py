from rest_framework import serializers
from .models import Company, Storage, Supplier, Product, SupplyProduct, Supply

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'company')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'quantity')


class SupplyProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = SupplyProduct
        fields = '__all__'


class SupplySerializer(serializers.ModelSerializer):
    products = SupplyProductSerializer(many=True, source='supply_products')
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )

    class Meta:
        model = Supply
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def validate_product(self, value):
        if not value:
            raise serializers.ValidationError("Должен быть хотя бы один товар в поставке")
        return value


class AddEmployeesSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()