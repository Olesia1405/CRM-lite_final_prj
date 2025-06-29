from rest_framework import serializers
from companies.serializers import CompanySerializer
from .models import User

class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

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