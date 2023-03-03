
from authentication.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import (CreateAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from utils.base.general import (generate_email_message, generate_otp,
                                get_tokens_for_user)

from . import serializers


class TokenVerifyAPIView(APIView):
    """
    An authentication plugin that checks if a jwt
    access token is still valid and returns the user info.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=serializers.JWTTokenValidateSerializer,
        responses={200: serializers.UserSerializer}
    )
    def post(self, request, format=None):
        jwt_auth = JWTAuthentication()

        raw_token = request.data.get('token')

        validated_token = jwt_auth.get_validated_token(raw_token)

        user = jwt_auth.get_user(validated_token)

        serialized_user = serializers.UserSerializer(user)
        user_details = serialized_user.data

        return Response(data=user_details)


class EmaiOtpMixin:

    email_template_name: str = 'authentication/email/verify_email.html'

    def get_email_template(self):
        return self.email_template_name

    def verify_user(self, user: User, context: dict = None):
        otp = generate_otp()

        if context is None:
            context = {}

        context.update({
            'name': user.profile.fullname,
            'otp': otp,
        })

        message = generate_email_message(
            self.get_email_template(),
            context,
        )

        user.mail(
            subject='Email Verification One Time Password',
            message=message,
        )

        return otp

    def verify_response(self, user: User):
        otp = self.verify_user(user)
        return Response(
            data={
                'email': user.email,
                'otp': otp,
            },
        )


class VerifyEmail(EmaiOtpMixin, APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=serializers.VerifiyEmail,
        responses={
            200: serializers.VerifiyEmail,
        }
    )
    def post(self, request, format=None):
        serializer = serializers.VerifiyEmail(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        return self.verify_response(user)


class TokenRefreshAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(
        request_body=TokenRefreshSerializer,
        responses={200: TokenRefreshSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginAPIView(EmaiOtpMixin, APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.LoginSerializer

    @swagger_auto_schema(
        request_body=serializers.LoginSerializer,
        responses={
            200: serializers.LoginResponseSerializer,
            423: serializers.VerifiyEmail
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        if user.verified_email:
            response_data = {
                'tokens': get_tokens_for_user(user),
                'user': serializers.UserSerializer(user).data
            }
            return Response(data=response_data)
        else:
            otp = self.verify_user(user)
            return Response(
                data={
                    'email': user.email,
                    'otp': otp,
                },
                status=status.HTTP_423_LOCKED
            )


class RegisterAPIView(EmaiOtpMixin, CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return self.verify_response(user)

    @swagger_auto_schema(
        request_body=serializers.RegisterSerializer,
        responses={201: serializers.VerifiyEmail}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ForgetPasswordView(EmaiOtpMixin, APIView):
    permission_classes = (AllowAny,)
    email_template_name = 'authentication/email/forget_password.html'

    @swagger_auto_schema(
        request_body=serializers.VerifiyEmail,
        responses={
            200: serializers.VerifiyEmail,
        }
    )
    def post(self, request, format=None):
        serializer = serializers.VerifiyEmail(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        return self.verify_response(user)


class UpdatePasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ForgetChangePasswordSerializer

    @swagger_auto_schema(
        request_body=serializers.ForgetChangePasswordSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update()
        return Response(data={'message': 'Password updated successfully'})


class ChangePasswordView(UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(active=True)


class UserRetrieveView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.filter

    def get_object(self):
        return self.request.user
