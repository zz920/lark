import uuid
from django.conf import settings 
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class LarkUser(User):
    """
    Overwrite the auth.models.User class with avtar feature.
    Username and password are required. Other field are optional.
    Fields:
        username : CharField
        password : CharField
        last_login : DateTimeField, default blank
        first_name : CharField, default blank
        last_name : CharField, default blank
        email : EmailField, default blank
        groups : Many to many relationship to Group
        user_permission : Many to many relationship to Permission
        is_staff : BooleanField, default False
        is_active : BooleanField, default True
        is_superuser : BooleanField, default False
        date_joined : DateTimeField, default now
        avatar : ImageField, default blank
    """

    avatar = models.ImageField(upload_to=settings.MEDIA_ROOT, blank=True)

    def upload_avatar(self, pic_file, upload_to=settings.MEDIA_ROOT):
        # to implement
        pass


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

