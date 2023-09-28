from django.db import models
from django.core.mail import send_mail
# Create your models here.
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
# _ is used in default fields to convert them into other languages
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


# CREATING TWO TYPES OF USER
class CustomAccountManger(BaseUserManager):
    
    def create_superuser(self,email,user_name,password,**other_fields):
        
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_active',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, password, **other_fields)
    
    def create_user(self,email,user_name,password,**other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        
        # validate the email
        email = self.normalize_email(email)
        # create an user
        user = self.model(email=email,user_name=user_name,**other_fields)
        user.set_password(password)
        user.save()
        return user

# creating a new user table for our users instead of building on the 
class UserBase(AbstractBaseUser,PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150,unique=True)
    first_name = models.CharField(max_length=150,blank=True)
    about = models.TextField(('about'), max_length=500, blank=True)
    
    # Delivery Details
    country = CountryField()
    phone_number = models.CharField(max_length=15, blank=True)
    postcode = models.CharField(max_length=12, blank=True)
    address_line_1 = models.CharField(max_length=150, blank=True)
    address_line_2 = models.CharField(max_length=150, blank=True)
    town_city = models.CharField(max_length=150, blank=True)
    
    # User Status
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # using to save the actual user
    objects = CustomAccountManger()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    # for admin.py to call the Class
    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            'l@1.com',
            [self.email],
            fail_silently=False,
        )

    # to help print the class
    def __str__(self):
        return self.user_name



