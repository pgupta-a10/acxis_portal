from django.conf.urls import url

from django.conf.urls import include, url
from portal.views import *

urlpatterns = [
    url(r'customer/', customer_view, name="customer_index"),
    url(r'global/$', global_view, name="global_index"),

    url(r'index/$', index, name="index"),
    url(r'load_apps/(?P<customer_id>[\w|\W]+)/(?P<account_type>[\w|\W]+)/$', load_apps, name="load_apps"),

    url(r'employee/login/$', employee_login, name="employee_login"),
    url(r'login/$', acxis_login, name="acxis_login"),

    url(r'callback/$', acxis_callback, name="acxis_callback"),
    url(r'customer/(?P<customer_id>[\w|\W]+)/$', customer_view, name="redirect_customer"),
]