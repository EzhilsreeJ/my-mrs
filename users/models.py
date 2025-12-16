from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator("Enter a valid email address.")],
        error_messages={'unique': "A user with that email already exists."},
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = 'email' # Use email as the primary identifier
    REQUIRED_FIELDS = ['username'] # Username is still required for some Django internals, but not for login

    def __str__(self):
        return self.email