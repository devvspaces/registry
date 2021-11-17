from os import stat
from re import sub
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi

from project_api_key.permissions import HasStaffProjectAPIKey

from authentication.tokens import account_confirm_token
from authentication.models import User, Phone
from authentication.utils import random_otp
from authentication.permissions import IsAuthenticatedAdmin
from authentication.models import Relationship

from . import serializers
from .utils import CustomError, get_tokens_for_user, send_email, send_sms


# Views below

class TokenVerifyAPIView(APIView):
    """
    An authentication plugin that checks if a jwt access token is still valid and returns the user info.
    """

    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    @swagger_auto_schema(
        request_body=serializers.JWTTokenValidateSerializer,
        responses={200: serializers.UserSerializer}
        )
    def post(self, request, format=None):

        jwt_auth = JWTAuthentication()

        raw_token = request.POST.get('token')

        validated_token = jwt_auth.get_validated_token(raw_token)

        user = jwt_auth.get_user(validated_token)

        serialized_user = serializers.UserSerializer(user)
        user_details = serialized_user.data

        return Response(user_details, status=status.HTTP_200_OK)


# Creating Api keys
class ProjectCreateAPIView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ProjectApiSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        # If email is passed in the post use that instead
        email = request.POST.get('email', False)
        if email:
            # Let's get the user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User provided does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user

            if not user.is_authenticated:
                return Response({'error': 'Provide a user email to create api for'}, status=status.HTTP_400_BAD_REQUEST)


        valid = serializer.is_valid()

        if valid:
            obj = serializer.save(user=user)

            # Get the sec key from the obj and pass to a variable then remove it
            pass_key = obj.demo_sec
            obj.demo_sec = ''
            obj.save()

            # Get the details with of the obj in dict form with the serializer
            obj_dict = serializers.ProjectApiSerializer(obj)
            api_details = obj_dict.data

            return Response({
                'secret_api_key': pass_key,
                'api_details': api_details
                }, status=status.HTTP_200_OK)

        return Response({'error': 'Your request could not be processed'}, status=status.HTTP_400_BAD_REQUEST)


class GenerateTokenView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    @swagger_auto_schema(
        query_serializer=serializers.TokenGenerateSerializer,
        responses={200: serializers.TokenGenerateResponseSerializer, 400: serializers.ErrorSerializer}
        )
    def get(self, request, format=None):
        # Get required info from the request handler
        pk = request.query_params.get('id', '')

        if not pk:
            error = CustomError(type='RequestError', code='req-001', request=request)
            return error.response()

        # Get the user from the pk
        try:
            user  = User.objects.get(id=pk)
        except (User.DoesNotExist, ValueError):
            error = CustomError(type='ObjectNotFound', code='user-001', request=request)
            return error.response()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_confirm_token.make_token(user)

        return Response({
            'uidb64': uidb64,
            'token': token
        }, status=status.HTTP_200_OK)


class ValidateTokenView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    @swagger_auto_schema(
        request_body=serializers.TokenGenerateResponseSerializer,
        responses={200: serializers.UserSerializer, 400: serializers.ErrorSerializer}
    )
    def post(self, request, format=None):
        # Get the uid and token from the data passed
        uidb64 = request.data.get('uidb64', '')
        token = request.data.get('token', '')

        try:
            uidb64=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            error = CustomError(type='TokenValidationError', code='user-003', request=request)
            return error.response()

        if user!=None:
            if user.confirmed_email:
                error = CustomError(type='TokenValidationError', code='user-002', request=request)
                return error.response()

            if account_confirm_token.check_token(user,token):
                user.confirmed_email=True
                user.save()

                s2=serializers.UserSerializer(user)
                user_details = s2.data

                return Response(user_details, status=status.HTTP_200_OK)
        else:
            error = CustomError(type='TokenValidationError', code='user-001', request=request)
            return error.response()


class GenerateOtpView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)

    @swagger_auto_schema(
        responses={200: serializers.OtpSerializer, 400: serializers.ErrorSerializer}
    )
    def get(self, request, format=None):
        # Generate a random otp
        otp = random_otp()
        
        return Response({
            'otp': otp
        }, status=status.HTTP_200_OK)


class TokenRefreshView(TokenRefreshView):
    permission_classes = (HasStaffProjectAPIKey,)
    # serializer_class = TokenRefreshLifetimeSerializer

class LoginAPIView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            user = User.objects.get(email=email)

            if user.is_active:
                if user.confirmed_email:
                    # Get the user details with the user serializer
                    s2=serializers.UserSerializer(user)
                    # s2.is_valid()
                    user_details = s2.data
                    return Response({
                        'tokens': get_tokens_for_user(user),
                        'user': user_details
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User email is not yet verified'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Account has been deactivated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPIView(CreateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.RegisterSerializer


class CreateUpdateUser(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializerObj

    def post(self, request, format=None):
        email = request.data.get('email')

        if not email:
            error = CustomError(type='RequestError', code='req-003', request=request)
            return error.response()

        try:
            # Check if user already exists
            user = User.objects.get(email=email)

            if user.has_usable_password():
                error = CustomError(type='RequestError', code='req-103', request=request)
                return error.response()
            else:
                serializer = serializers.UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            # Create user
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationshipCreateAPIView(APIView):
    permission_classes = ((HasStaffProjectAPIKey & IsAuthenticated) | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializerObj
    
    @swagger_auto_schema(
        request_body=serializers.RelationshipMadeSerializer,
        responses={201: serializers.RelationshipSerializer}
    )
    def post(self, request, format=None):
        """
        A user can be created or gotten and sent a relationship request with this endpoint, all you need to do is pass the email
        and phone numbers of the user to the request.
        Phone numbers (phones) will be a single phone number or comma separated phone numbers.

        After successful creation of a user, emails and sms will be sent to the user to make he/she download the app and complete the registration
        process then verify relationship.
        """
        email = request.data.get('email')
        phones = request.data.get('phones')

        if not email:
            error = CustomError(type='RequestError', code='req-003', request=request)
            return error.response()
        
        if not phones:
            error = CustomError(type='RequestError', code='req-004', request=request)
            return error.response()

        try:
            # Check if user already exists
            user = User.objects.get(email=email)

            if user.has_usable_password():
                error = CustomError(type='RequestError', code='req-103', request=request)
                return error.response()

        except User.DoesNotExist:
            # Create user
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                user = User.objects.create(email=serializer.data.get('email'))
                user.set_unusable_password()
                user.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        obj = Relationship.objects.create(creator=request.user, other=user, phone_numbers=phones)
        serializer = serializers.RelationshipSerializer(obj)

        message_to_send = ''

        # Send email
        send_email(email=user.email, subject='Requested Relationship on Registry', message=message_to_send)

        # Send sms
        phones_list = []
        for i in phones.split(','):
            phones_list.append(i.strip())

        for phone in phones_list:
            send_sms(message_to_send, phone)

        # Send messages and email to user added
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateUpdateUser(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializerObj

    def post(self, request, format=None):
        email = request.data.get('email')

        if not email:
            error = CustomError(type='RequestError', code='req-003', request=request)
            return error.response()

        try:
            # Check if user already exists
            user = User.objects.get(email=email)

            if user.has_usable_password():
                error = CustomError(type='RequestError', code='req-103', request=request)
                return error.response()
            else:
                serializer = serializers.UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except User.DoesNotExist:
            # Create user
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class RelationshipCreateAPIView(CreateAPIView):
#     permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
#     serializer_class = serializers.RelationshipSerializer

class PhoneCreateAPIView(CreateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.PhoneSerializer

class PhoneListAPIView(ListAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.PhoneSerializer

    @swagger_auto_schema(
        query_serializer=serializers.UserSeriy,
        # responses={200: serializers.PhoneSerializer}
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_queryset(self):
        user = self.request.query_params.get('user', '')
        queryset = Phone.objects.all()

        if user:
            queryset = queryset.filter(user=user)
            
        return queryset


class PhoneUpdateAPIView(UpdateAPIView):
    lookup_field = 'id'
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.PhoneSerializer

    def get_queryset(self):
        return Phone.objects.all()


class SetPasswordView(UpdateAPIView):
    permission_classes = ((HasStaffProjectAPIKey & IsAuthenticated) | IsAuthenticatedAdmin,)
    serializer_class = serializers.ForgetChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.filter(active=True)


class ChangePasswordView(UpdateAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.ChangePasswordSerializer

    def get_object(self):
        try:
            obj = self.get_queryset().get(id=self.request.user.id)
            return obj
        except (User.DoesNotExist, ValueError):
            raise NotFound(detail='User does not exist')

    def get_queryset(self):
        return User.objects.filter(active=True)


class UserListView(ListAPIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by('first_name')


class UserAPIView(RetrieveUpdateAPIView):
    lookup_field = 'id'
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all()
    
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user is not None:
            return Response(self.get_serializer_class()(user).data)

        error = CustomError(type='ObjectNotFound', code='user-001', request=request)
        return error.response()


class SendMailView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.SendMailSerializer

    @swagger_auto_schema(
        request_body=serializers.SendMailSerializer,
        responses={200: serializers.SendMailResponseSerializer, 400: serializers.ErrorSerializer}
    )
    def post(self, request, format=None):
        """
        Send message and subject to the passed email
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Get the email
            email = serializer.data.get('email')
            subject = serializer.data.get('subject')
            message = serializer.data.get('message')
            sent = send_email(email, subject, message)
            
            return Response({
                'email': email,
                'sent': sent
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendSmsView(APIView):
    permission_classes = (HasStaffProjectAPIKey | IsAuthenticatedAdmin,)
    serializer_class = serializers.SendSmsSerializer

    @swagger_auto_schema(
        request_body=serializers.SendSmsSerializer,
        responses={200: serializers.SendSmsResponseSerializer, 400: serializers.ErrorSerializer}
    )
    def post(self, request, format=None):
        """
        Send sms message to the passed phone no
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Get the email
            phone = serializer.data.get('phone')
            message = serializer.data.get('message')
            sent = send_sms(message, phone)
            
            return Response({
                'sent': sent
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

