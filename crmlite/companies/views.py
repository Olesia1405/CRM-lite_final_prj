from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework.exceptions import PermissionDenied
from .models import Company, Storage, Supplier, Product, Supply, SupplyProduct
from .serializers import (CompanySerializer, StorageSerializer,
                          SupplierSerializer, ProductSerializer, SupplyCreateSerializer,
                          SupplySerializer, AddEmployeesSerializer)
from users.models import User
from .permissions import IsCompanyOwner, IsCompanyEmployee

@extend_schema(
    tags=['Companies'],
    description='Создает новую компанию',
    request=CompanySerializer,
    responses={
        201: OpenApiResponse(
            response=CompanySerializer,
            description='Компания успешно создана',
            examples=[
                OpenApiExample(
                    'Пример успешного ответа',
                    value={
                        'id': 1,
                        'INN': '123456789012',
                        'title': 'Моя компания',
                        'description': 'Описание компании'
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Невалидные данные',
            examples=[
                OpenApiExample(
                    'Ошибка валидации данных',
                    value={
                        'INN': ['Это поле обязательно'],
                        'title': ['Это поле обязательно']
                    }
                )
            ]
        ),
        403: OpenApiResponse(
            description='Запрещено',
            examples=[
                OpenApiExample(
                    'Пользователь уже владелец компании',
                    value={
                        'detail': 'Вы уже являетесь владельцем компании'
                    }
                )
            ]
        )
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'INN': '123456789012',
                'title': 'Моя компания',
                'description': 'Описание моей компании'
            },
            request_only=True
        )
    ]
)
class CompanyCreateView(generics.CreateAPIView):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.is_company_owner:
            raise PermissionDenied("Вы уже являетесь владельцем компании")

        company = serializer.save()
        user = self.request.user
        user.is_company_owner = True
        user.company = company
        user.save()

@extend_schema(tags=["Companies"])
class CompanyDetailView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes =  [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsCompanyOwner()]

    def get_queryset(self):
        user = self.request.user
        return Company.objects.filter(employees=user)

@extend_schema(tags=["Storages"])
class StorageView(generics.ListCreateAPIView):
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyEmployee]

    def get_queryset(self):
        user = self.request.user
        if not user.company:
            return Storage.objects.none()
        return Storage.objects.filter(company=user.company)

    def perform_create(self, serializer):
        if not self.request.user.is_company_owner:
            raise PermissionDenied("Only company owner can create storages")
        serializer.save(company=self.request.user.company)

@extend_schema(tags=["Storages"])
class StorageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsCompanyOwner()]

    def get_queryset(self):
        user = self.request.user
        if not user.company:
            return Storage.objects.none()
        return Storage.objects.filter(company=user.company)


@extend_schema(
    tags=['Suppliers'],
    examples=[
        OpenApiExample(
            'Пример создания поставщика',
            value={
                "name": "ООО Поставщик",
                "contact_person": "Иванов Иван",
                "phone": "+79991234567",
                "email": "supplier@mail.com",
                "address": "Москва, ул. Примерная, 1"
            },
            request_only=True
        )
    ]
)
class SupplierListView(generics.ListCreateAPIView):
    """
    GET: Список поставщиков компании (для всех сотрудников)
    POST: Создание поставщика (только для владельца)
    """
    serializer_class = SupplierSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsCompanyOwner()]
        return [permissions.IsAuthenticated(), IsCompanyEmployee()]

    def get_queryset(self):
        return Supplier.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]

    def get_queryset(self):
        return Supplier.objects.filter(company=self.request.user.company)


@extend_schema(tags=["Products"])
class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(storage__company=self.request.user.company)
        storage_id = self.request.query_params.get('storage_id')
        if storage_id:
            queryset = queryset.filter(storage_id=storage_id)
        return queryset


    def perform_create(self, serializer):
        storage = serializer.validated_data['storage']
        if storage.company != self.request.user.company:
            raise PermissionDenied('Вы не можете добавлять товары на этот склад')
        serializer.save(quantity=0)

@extend_schema(tags=["Products"])
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(storage__company=self.request.user.company)


@extend_schema(tags=["Supplies"])
class SupplyCreateView(generics.CreateAPIView):
    serializer_class = SupplyCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]

    @transaction.atomic
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        products_data = validated_data.pop('products', [])

        supply = Supply.objects.create(
            **validated_data,
            created_by=self.request.user
        )

        for product_item in products_data:
            product = get_object_or_404(
                Product,
                id=product_item['product_id'],
                storage__company=self.request.user.company
            )

            SupplyProduct.objects.create(
                supply=supply,
                product=product,
                quantity=product_item['quantity'],
                purchase_price=product.purchase_price
            )

            product.quantity += product_item['quantity']
            product.save()

        return supply


@extend_schema(tags=["Supplies"])
class SupplyListView(generics.ListAPIView):
    serializer_class = SupplySerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyEmployee]

    def get_queryset(self):
        return Supply.objects.filter(
            storage__company=self.request.user.company
        ).prefetch_related(
            Prefetch(
                'supply_products',
                queryset=SupplyProduct.objects.select_related('product')
            )
        ).select_related('supplier', 'storage', 'created_by').order_by('-created_at')


@extend_schema(
    tags=['Employees'],
    description='''
    Добавление сотрудника в компанию.
    Требуются права владельца компании.
    Можно указать либо user_id, либо email.
    ''',
    examples=[
        OpenApiExample(
            'Example by ID',
            value={"user_id": 3},
            request_only=True
        ),
        OpenApiExample(
            'Example by email',
            value={"email": "user@example.com"},
            request_only=True
        )
    ]
)
class AddEmployeeView(generics.GenericAPIView):
    serializer_class = AddEmployeesSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            email=serializer.validated_data['email']
        )

        if user.company:
            return Response(
                {'detail': 'Пользователь уже привязан к другой компании'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.company = request.user.company
        user.save()

        return Response(
            {
                'detail': 'Пользователь успешно добавлен в компанию',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                }
            },
            status=status.HTTP_200_OK
        )