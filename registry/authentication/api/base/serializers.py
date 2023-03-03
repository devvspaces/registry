from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from authentication.models import User, Phone, Relationship, Profile


class RelationshipMadeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phones = serializers.CharField()


class JWTTokenValidateSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserSeriy(serializers.Serializer):
    user = serializers.CharField()


class VerifiyEmail(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(read_only=True)
    user: User = None

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if not qs.exists():
            raise serializers.ValidationError(
                "Email does not exist in our database")
        user = qs.first()
        self.user = user
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    fullname = serializers.CharField(write_only=True, required=True)
    country = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'email', 'fullname', 'country')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        profile: Profile = user.profile
        profile.fullname = validated_data['fullname']
        profile.country = validated_data['country']
        profile.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    user: User = None

    def validate(self, attrs):
        # Get required info for validation
        email = attrs['email']
        password = attrs['password']

        """
        Check that the email is available in the User table
        """
        try:
            user: User = User.objects.get(email=email, active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": 'Your account is not active. \
Please contact support.'})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"email": 'Email and Password do not match'})

        self.user = user
        return attrs


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'verified_email',
            'active',
            'profile'
        )
        read_only_fields = (
            'email',
            'verified_email',
            'active',
        )


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    tokens = TokenSerializer()


class ForgetChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    user: User = None

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if not qs.exists():
            raise serializers.ValidationError(
                "Email does not exist in our database")
        user = qs.first()
        self.user = user
        return value

    def update(self):
        new_password = self.validated_data.get('password')
        self.user.set_password(new_password)
        self.user.save()
        return self.user


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('old_password', 'new_password',)

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(
                "Old password does not match")
        return value

    def update(self, instance, validated_data):
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()
        return instance
