from django.contrib.auth.password_validation import validate_password
from django.core import validators
from rest_framework import serializers

from authentication.models import User, Phone, Relationship
from authentication.utils import validate_phone

from project_api_key.models import ProjectApiKey



class RelationshipMadeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phones = serializers.CharField()

class JWTTokenValidateSerializer(serializers.Serializer):
    token = serializers.CharField()

class UserSeriy(serializers.Serializer):
    user = serializers.CharField()

class SendMailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField()
    message = serializers.CharField()


class SendSmsSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[validate_phone])
    message = serializers.CharField()

class SendSmsResponseSerializer(serializers.Serializer):
    sent = serializers.BooleanField()


class SendMailResponseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    sent = serializers.BooleanField()

class OtpSerializer(serializers.Serializer):
    otp = serializers.IntegerField()

class TokenGenerateSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class TokenGenerateResponseSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    error = serializers.CharField()
    code = serializers.CharField()
    message = serializers.CharField()
    path = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class UserSerializerObj(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Get required info for validation
        email = attrs['email']
        password = attrs['password']

        """
        Check that the email is available in the User table
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": 'Details do not match an active account'})
        
        if not user.check_password(password):
            raise serializers.ValidationError({"password": 'Your password is incorrect'})

        return attrs


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    Phone = PhoneSerializer(read_only=True)
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'Phone'
        ]



class ProjectApiSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ProjectApiKey
        fields = ['pub_key', 'user']



class ForgetChangePasswordSerializer(serializers.ModelSerializer):
    Phone = PhoneSerializer(read_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'new_password', 'confirm_password', 'Phone',)
        extra_kwargs = {
            'first_name': {'read_only': True},
            'email': {'read_only': True},
            'last_name': {'read_only': True},
        }
        
    def validate(self, attrs):
        # Validate if the provided passwords are similar
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})

        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()

        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    Phone = PhoneSerializer(read_only=True)
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'old_password', 'new_password', 'confirm_password', 'Phone',)
        extra_kwargs = {
            'first_name': {'read_only': True},
            'email': {'read_only': True},
            'last_name': {'read_only': True},
        }
        
    def validate(self, attrs):
        if not self.instance.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Old password is not correct'})

        # Validate if the provided passwords are similar
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})

        return attrs

    def update(self, instance, validated_data):
        # Set password
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()

        return instance