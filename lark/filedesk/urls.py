from django.conf.urls import url
from filedesk import views
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^home$', TemplateView.as_view(template_name='filedesk_base.html'), name="filedesk_index"),
]
