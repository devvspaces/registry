from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserRegisterForm
from .models import Phone, User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserUpdateForm
    add_form = UserRegisterForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'active',)
    list_filter = ('active', 'staff', 'admin',)
    search_fields = ('email',)
    fieldsets = (
        ('User', {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('admin', 'staff', 'active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2')
        }
        ),
    )
    ordering = ('-start_date',)
    filter_horizontal = ()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'country', 'sex')
    search_fields = ('fullname',)
    list_filter = ('sex',)
    fieldsets = (
        (None, {
            "fields": (
                'user',
                "fullname",
            )
        }),
    )


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('phoneno', 'profile',)
    search_fields = ('phoneno', 'profile__fullname')
    list_filter = ('profile__sex',)
