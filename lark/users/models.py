import uuid

from django.conf import settings 
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator


class LarkUserManager(BaseUserManager):
    """
    Rewrite the default UserManager, use emails as the unique identifier for 
    auth instead of usernames.
    """

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and save a LarkUser with the given username, email and password
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(username, email, password, **extra_fields)


class LarkUser(AbstractUser):
    """
    Overwrite the auth.models.User class with avtar feature.
    Email is the unique identifier for user.
    Fields:
        email : CharField
        username : CharField
        password : CharField
        last_login : DateTimeField, default blank
        first_name : CharField, default blank
        last_name : CharField, default blank
        groups : Many to many relationship to Group
        user_permission : Many to many relationship to Permission
        is_staff : BooleanField, default False
        is_active : BooleanField, default True
        is_superuser : BooleanField, default False
        date_joined : DateTimeField, default now
        avatar : ImageField, default blank
    """
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
    )
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to=settings.MEDIA_ROOT, blank=True)

    """
    Reset the UserManager
    """
    objects = LarkUserManager()
    
    """
    Reset email as the unique identifier
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def upload_avatar(self, pic_file, upload_to=settings.MEDIA_ROOT):
        # to implement
        pass

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

class ServerTable(models.Model):
    """
    User server list
    """
    server_id = models.UUIDField(primary_key=True,
                                 default=uuid.uuid4,
                                 editable=False)
    ip_address = models.GenericIPAddressField(protocol='both',
                                              unpack_ipv4=False,
                                              unique=True)
    port = models.IntegerField(validators=[MaxValueValidator(65535),
                                           MinValueValidator(0)])
    owner = models.ForeignKey(LarkUser, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(ServerTable, self).__init__(*args, **kwargs)

    def verfy_connection(self):
        pass



