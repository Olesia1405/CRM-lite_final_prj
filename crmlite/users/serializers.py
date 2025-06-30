from rest_framework import serializers
from .models import User
from companies.models import Company


class UserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    def get_company(self, obj):
        from companies.serializers import CompanySerializer  # Ленивый импорт
        return CompanySerializer(obj.company).data if obj.company else None

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_company_owner', 'company')
        extra_kwargs = {'password': {'write_only': True}}


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user