from typing import TypeVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.base.validators import validate_phone, validate_special_char
from utils.base.general import send_email

import random

T = TypeVar('T', bound=AbstractBaseUser)


class UserManager(BaseUserManager):
    def create_base_user(
        self, email, is_active=True,
        is_staff=False, is_admin=False
    ) -> T:
        if not email:
            raise ValueError("User must provide an email")

        user: User = self.model(
            email=self.normalize_email(email)
        )
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(
        self, email, password=None, is_active=True,
        is_staff=False, is_admin=False
    ) -> T:
        user = self.create_base_user(email, is_active, is_staff, is_admin)
        if not password:
            raise ValueError("User must provide a password")
        user.set_password(password)
        user.save()
        return user

    def create_staff(self, email, password=None) -> T:
        user = self.create_user(email=email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None) -> T:
        user = self.create_user(
            email=email, password=password, is_staff=True, is_admin=True)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    verified_email = models.BooleanField(default=False)

    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["first_name", "last_name"]
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def mail(self, subject, message, fail=True):
        val = send_email(
            email=self.email, subject=subject, message=message, fail=fail
        )
        return True if val else False

    def verify_otp(self, otp: int):
        """
        Validate the otp
        """
        return self.otp == otp

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = 'User'


class Profile(models.Model):
    SEX = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fullname = models.CharField(
        max_length=50, validators=[validate_special_char])
    sex = models.CharField(
        choices=SEX, max_length=1, blank=True)
    country = models.CharField(max_length=60, blank=True)

    def __str__(self) -> str:
        return self.fullname


class Phone(models.Model):
    phoneno = models.CharField(
        max_length=16,
        validators=[validate_phone],
        help_text='Enter a correct phone number',
    )
    verified = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.phoneno


class PendingRelationship(models.Model):
    creator = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='creator')
    name = models.CharField(max_length=50, validators=[validate_special_char])
    country = models.CharField(max_length=60, blank=True)

    def connect(self, profile: Profile):
        partner = Partner.objects.create(
            profile=profile,
            pending_relationship=self,
            partner=self.creator.partner
        )
        return partner

    def connect_without_profile(self):
        return self.connect(None)

    def __str__(self) -> str:
        return self.name


class PendingRelationshipPhone(models.Model):
    phoneno = models.CharField(
        max_length=16,
        validators=[validate_phone],
        help_text='Enter a correct phone number',
    )
    verified = models.BooleanField(default=False)
    pending_relationship = models.ForeignKey(
        PendingRelationship, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.phoneno


class Partner(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, null=True)
    pending_relationship = models.ForeignKey(
        PendingRelationship, on_delete=models.CASCADE, null=True)
    partner = models.ForeignKey("self", on_delete=models.CASCADE, null=True)

    def get_name(self):
        if self.profile:
            return self.profile.fullname
        if self.pending_relationship:
            return self.pending_relationship.name
        raise ValueError('Partner must have a profile or pending relationship')

    def __str__(self) -> str:
        return self.get_name()


class Relationship(models.Model):
    RELATIONSHIP_STATUS = [
        ('dating', 'Dating',),
        ('married', 'Married',),
    ]

    partners = models.ManyToManyField(
        Partner, validators=[lambda x: x.count() == 2])
    status = models.CharField(
        choices=RELATIONSHIP_STATUS, max_length=10, default='dating')
    verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        first: Partner = self.partners.first()
        if first == self.partners.last():
            return f'{first.get_name()} & Not Verified'
        return f'{first.get_name()} & \
{self.partners.last().get_name()}'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
