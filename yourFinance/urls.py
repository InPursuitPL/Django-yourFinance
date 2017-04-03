from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/register/$', views.register_page, name='register'),
    url(r'set_date/$', views.set_date, name='set date'),
    url(r'(?P<date>.+)/$', views.show_date, name='show date'),
    url(r'^add_data/$', views.add_data, name='add data'),
    url(r'^view_all_data/$', views.view_all_data, name = 'view all data'),
]
