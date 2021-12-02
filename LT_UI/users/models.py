from django.db import models
from django.contrib.auth import hashers, models as auth_models
from django.utils import crypto


# Create your models here.
class User(auth_models.AbstractUser):
    """
    User model for extending later
    """
    verified = models.BooleanField(default=False)


def default_code():
    return crypto.get_random_string(20)


class Code(models.Model):
    """
    Holds codes for verifying users
    """
    code = models.CharField(max_length=200, default=default_code,  
        help_text="Make sure to copy this code since it won't be visible later")
    timeout = models.DateTimeField(blank=False, null=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            print(self.code)
            self.code = hashers.make_password(self.code)
            print(self.code)
        return super().save(*args, **kwargs)

    def check_code(self, code):
        return hashers.check_password(code, self.code)
