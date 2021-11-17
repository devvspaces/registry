from django.forms import ValidationError
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .utils import get_usable_name, validate_phone, regex_phone
from .validators import validate_special_char


class UserManager(BaseUserManager):
    def create_user(self, email=None, first_name=None, last_name=None, password=None, is_active=False, is_staff=False,
                    is_admin=False, *args, **kwargs):
        if not email:
            raise ValueError("Email is required")
        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if not password:
            raise ValueError("Strong password is required")

        user = self.model(
            email = self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.save(using=self._db)

        return user

    def create_staff(self, email, first_name=None, last_name=None, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password, is_staff=True)
        return user

    def create_superuser(self, email, first_name=None, last_name=None, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password, is_staff=True,
                                is_admin=True, is_active=True)
        return user

    def get_staffs(self):
        return self.filter(staff=True)

    def get_admins(self):
        return self.filter(admin=True)


RELATIONSHIP_STATUS = [
    ('single', 'Single',),
    ('dating', 'Dating',),
    ('married', 'Married',),
]

class User(AbstractBaseUser):
    
    first_name = models.CharField(max_length=15, validators=[validate_special_char])
    last_name = models.CharField(max_length=15, validators=[validate_special_char])
    email = models.EmailField(max_length=255, unique=True)

    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=RELATIONSHIP_STATUS, max_length=20, default='single')

    # Confirmation fields
    confirmed_phoneno = models.BooleanField(default=False)
    confirmed_id = models.BooleanField(default=False)
    confirmed_address = models.BooleanField(default=False)
    confirmed_email = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["first_name","last_name"]
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, fail=True):
        print(message)
        val = send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[self.email], fail_silently=fail)
        return True if val else False

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
    
    @property
    def fullname(self):
        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'
    
    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = 'User'


class Phone(models.Model):
    phoneno = models.CharField(max_length=16,
        validators=[regex_phone],
        help_text='Enter a correct phone number',
        null=True,
        blank=True,
        unique=True,
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Override save method to validate phone field
    def save(self, *args, **kwargs):
        if self.phoneno:
            # First check if this password has been used by anyone
            exists = self.__class__.objects.filter(phoneno=self.phoneno).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError('This phone number has been used')
            
            # Validate your phone number
            phoneno = str(self.phoneno).replace(' ','')
            if not validate_phone(phoneno):
                raise ValidationError('Invalid phone number provided', code='invalid_phone')

        super().save(*args, **kwargs)
    

    def __str__(self) -> str:
        return self.phoneno


class Relationship(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='First_Partner')
    other = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Second_Partner')
    phone_numbers = models.CharField(max_length=300)
    verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user1.fullname} == {self.user2.fullname}"

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         username = get_usable_name(instance, Profile)
#         Profile.objects.create(user=instance)
