from authentication.models import User
from rest_framework.permissions import IsAuthenticated as IsAuthenticatedBase
from rest_framework_simplejwt.models import TokenUser


def set_user(request):
    # Check if the user is a Token user and set user to request
    if isinstance(request.user, TokenUser):
        try:
            # Get the user object from the database and must be active
            user = User.objects.get(id=request.user.id, active=True)
            request.user = user
        except User.DoesNotExist:
            raise Exception('Not a authenticated')


class IsAuthenticated(IsAuthenticatedBase):
    def has_permission(self, request, view):
        set_user(request)
        return super().has_permission(request, view)
