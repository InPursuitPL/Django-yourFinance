from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sample_user_login/$', views.sample_user_login, name='sample user login'),
    url(r'^accounts/register/$', views.register_page, name='register'),
    url(r'^view_profile/$', views.view_profile, name='view profile'),
    url(r'^add_data/$', views.add_data, name='add data'),
    url(r'^view_data/$', views.view_data, name='view data'),
    url(r'^data_edit/(?P<pk>\d+)$', views.data_edit, name='data edit'),
    url(r'^data_delete/(?P<pk>\d+)$', views.data_delete, name='data delete'),
    url(r'^delete_multiple_data/$', views.delete_multiple_data, name='delete multiple data'),
    url(r'^group_delete/(?P<date>.+)$', views.group_delete, name='group delete'),
    url(r'^analyze_data/$', views.analyze_data, name='analyze data'),
    url(r'^(?P<date>.+)/analyze_record/$', views.analyze_record, name='analyze record'),
    url(r'^configure_deposition_places/$',
        views.configure_deposition_places,
        name='configure deposition places'),
    url(r'^configure_monthly_costs/$',
        views.configure_monthly_costs,
        name='configure monthly costs'),
    url(r'^configure_cost_groups/$',
        views.configure_cost_groups,
        name='configure cost groups'),
]
