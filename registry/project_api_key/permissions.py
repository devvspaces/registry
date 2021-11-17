from rest_framework import permissions

from django.utils.crypto import get_random_string
from django.conf import settings

from .models import ProjectApiKey


class HasStaffProjectAPIKey(permissions.BasePermission):
    
    """
    This is a permission class to validate api keys
    """

    def has_permission(self, request, view):
        print('Hey got to the python code in the section')

        key, api_obj = self.validate_apikey(request)

        if key:
            return (api_obj.user.staff or api_obj.user.admin)

    def validate_apikey(self, request):
        custom_header = settings.API_KEY_HEADER
        custom_sec_header = settings.API_SEC_KEY_HEADER

        pub_key = self.get_from_header(request, custom_header)
        sec_key = self.get_from_header(request, custom_sec_header)

        # The the Project api key obj the pub_key belongs to
        try:
            api_obj = ProjectApiKey.objects.get(pub_key=pub_key)
        except ProjectApiKey.DoesNotExist as e:
            return False, None

        return api_obj.check_password(sec_key), api_obj

    def get_from_header(self, request, name):
        return request.META.get(name) or None