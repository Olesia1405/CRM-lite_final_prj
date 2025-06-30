from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Company, Storage, Supplier, Product, SupplyProduct, Supply
from django.contrib.auth import get_user_model

User = get_user_model()

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
        read_only_fields = ('purchase_price',)


class SupplySerializer(serializers.ModelSerializer):
    products = SupplyProductSerializer(many=True, source='supply_products', required=True)
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )
    storage_id = serializers.PrimaryKeyRelatedField(
        queryset=Storage.objects.all(),
        source='storage',
        write_only=True
    )
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Supply
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Должен быть хотя бы один товар в поставке")

        for product_data in value:
            if product_data.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    f"Количество товара {product_data.get('product_id')} должно быть положительным"
                )
            product = product_data['product']
            if product.storage.company != self.context['request'].user.company:
                raise serializers.ValidationError(
                    f"Товар {product.id} не принадлежит вашей компании"
                )

        return value

    def validate(self, data):
        products_data = data.get('supply_products')

        for product_data in products_data:
            product = product_data['product']
            product_data.setdefault('purchase_price', [])

        return data

    def create(self, validated_data):
        products_data = validated_data.pop('supply_products', [])
        supply = Supply.objects.create(**validated_data)

        for product_data in products_data:
            SupplyProduct.objects.create(
                supply=supply,
                **product_data
            )

            product = product_data['product']
            product.quantity += product_data['quantity']
            product.save()

        return supply


class AddEmployeesSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, data):
        if not any([data.get('user_id'), data.get('email')]):
            raise serializers.ValidationError("Необходимо указать user_id или email")

        user = self.get_user()

        if user.is_company_owner:
            raise serializers.ValidationError('Нельзя прикрепить владельца другой компании')

        self.context['user'] = user

        return data

    def get_user(self):
        from users.models import User

        if self.validated_data.get('user_id'):
            return get_object_or_404(User, id=self.validated_data['user_id'])
        elif self.validated_data.get('email'):
            return get_object_or_404(User, email=self.validated_data['email'])