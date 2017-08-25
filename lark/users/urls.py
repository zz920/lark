from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^signup$', views.user_signup, name='signup'),
    url(r'^signin$', views.user_signin, name='signin'),
    url(r'^signout$', views.user_signout, name='signout'),
]
