from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/register/$', views.register_page, name='register'),
    url(r'^add_data/$', views.add_data, name='add_data'),
    url(r'^view_all_data/$', views.view_all_data, name = 'view all data'),
]
