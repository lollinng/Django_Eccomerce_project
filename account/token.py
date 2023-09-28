from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

"""
Django has passwordReset tokens which can be used to check the 
validity of the user email and checking the token send through mail
for his registration
"""

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.is_active)
        )
    
account_activation_token = AccountActivationTokenGenerator()