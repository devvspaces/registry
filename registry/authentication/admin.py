from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserRegisterForm
from .models import User, Phone

class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	# form = UserUpdateForm
	add_form = UserRegisterForm

	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display=('email', 'active',)
	list_filter = ('active','staff','admin',)
	search_fields=('email', 'first_name', 'last_name',)
	fieldsets = (
		('User', {'fields': ('email', 'password')}),
		('Permissions', {'fields': ('admin','staff','active',)}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'first_name', 'last_name', 'password', 'password2')}
		),
	)
	ordering = ('-start_date',)
	filter_horizontal = ()

class PhoneAdmin(admin.ModelAdmin):
	list_display=('phoneno', 'user',)
	search_fields=['phoneno']
	fieldsets=(
		(None, {
			"fields": (
				'user',
				"phoneno",
			)
		}),
	)

admin.site.register(User, UserAdmin)

admin.site.register(Phone, PhoneAdmin)