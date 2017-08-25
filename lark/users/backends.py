from django.utils import timezone
from django.contrib.auth import backends
from django.conf import settings


class LarkBackend(backends.ModelBackend):
    """
    Rewrite django.contrib.auth.ModelBackend to authenticate a user with unique 
    email address and password.
    https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#authentication-backends
    """
    
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Except new registed user within 3-days.
        """
        is_active = getattr(user, 'is_active', None)
        date_joined = getattr(user, 'date_joined', None)
 
        return is_active or self.check_time_delay(date_joined)

    def check_time_delay(self, join_date):
        """
        Verify the time delay before email confirmation
        """

        now = timezone.now()
        return now - join_date < settings.REGISTER_DELAY
