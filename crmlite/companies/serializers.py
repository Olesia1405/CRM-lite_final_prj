from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Company, Storage, Supplier, Product, SupplyProduct, Supply, Sale, ProductSale
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


class SupplyCreateProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(
        min_value=1,
        help_text="ID товара"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="Количество товара"
    )


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



class SupplyCreateSerializer(serializers.Serializer):
    storage_id = serializers.PrimaryKeyRelatedField(
        queryset=Storage.objects.all(),
        source='storage'
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        required=False
    )
    products = SupplyCreateProductSerializer(
        many=True,
        help_text='Список товаров в поставке'
    )

    def validate_products(self, value):
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Неверный формат товаров")
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Количество должно быть положительным")
        return value

class SupplySerializer(serializers.ModelSerializer):
    products = SupplyProductSerializer(many=True, source='supply_products', read_only=True)
    supplier = SupplierSerializer(read_only=True)
    storage = StorageSerializer(read_only=True)

    class Meta:
        model = Supply
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')


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
        if self.validated_data.get('user_id'):
            return get_object_or_404(User, id=self.validated_data['user_id'])
        elif self.validated_data.get('email'):
            return get_object_or_404(User, email=self.validated_data['email'])


class ProductSaleCreateSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product'
    )
    quantity = serializers.IntegerField(min_value=1)


class SaleCreateSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(
        max_length=255,
        required=True,
        help_text='Имя покупателя'
    )
    sale_date = serializers.DateTimeField(
        required=False,
        default_timezone=timezone.get_current_timezone(),
        help_text='Дата продажи'
    )
    product_sales = ProductSaleCreateSerializer(many=True)

    def validate(self, data):
        data.setdefault('sale_date', timezone.now())
        if not data['product_sales']:
            raise serializers.ValidationError("Должен быть хотя бы один товар в продаже")
        return data


class ProductSaleSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = ProductSale
        fields = ['id', 'product', 'product_title','quantity', 'price', 'created_at']
        read_only_fields = ('price', 'created_at')


class SaleSerializer(serializers.ModelSerializer):
    product_sales = ProductSaleSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.title', read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'