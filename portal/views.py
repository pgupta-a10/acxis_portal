# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from portal import acxis_elastic_interface
from app_loader import Acxis_apps
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import logging
import ldap
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.models import User
from django.contrib.auth import login
import requests
import json

log = logging.getLogger(__name__)


def logout(request):
    pass


def customer_view(request):
    customer_id = request.GET.get('customer_id', None)
    customer_name = ""
    customer_contact_person = ""
    account_type = ""

    if customer_id is None:
        customer_id = '0016000000G8UcB'

    rs = acxis_elastic_interface.get_customer(customer_id)
    if rs and len(rs) > 0:
        customer_obj = rs[0]
        customer_name = customer_obj['customer_name']
        customer_contact_person = customer_obj['customer_contact']
        account_type = customer_obj['account_type']


    return render(request, "customer_view.html",{
             'customer_name': customer_name,
             'customer_id': customer_id,
             'customer_contact_person': customer_contact_person,
             'customer_contact_phone': 'xxx-xxx-xxx',
            'account_person': 'Susan Ellis',
             'sales_person': 'Pallav Patil',
             'sales_engineer': 'John Doe'
    })


def global_view(request):

    selected_customer_id = request.GET.get('select_customer')
    customer_name = ""
    customer_contact_person = ""
    account_type = ""
    all_customers_dict = acxis_elastic_interface.get_aggregated_customers()

    #if customer_id is None:
        #customer_id = '0016000000G8UcB'
    if selected_customer_id:
        rs = acxis_elastic_interface.get_customer(selected_customer_id)
        if rs and len(rs) > 0:
            customer_obj = rs[0]
            customer_name = customer_obj['customer_name']
            customer_contact_person = customer_obj['customer_contact']
            account_type = customer_obj['account_type']

    return render(request, "global_view.html",{
        'customer_name': customer_name,
        'customer_id': selected_customer_id,
        'customer_contact_person': customer_contact_person,
        'customer_contact_phone': 'xxx-xxx-xxx',
        'account_person': 'Susan Ellis',
        'sales_person': 'Pallav Patil',
        'sales_engineer': 'John Doe',
        'all_customers_dict': all_customers_dict
    })


def index(request):
    pass


def load_apps(request, customer_id, account_type):
    if customer_id:
        pass
    else:
        # employee
        user = request.user
    apps = Acxis_apps.load_customer_apps()
    print apps


# def _start_app():
#     import threading
#     #from app_loader import Acxis_apps
#     import app_loader2
#     apps = Acxis_apps()
#     # print apps.started
#     if not apps.started:
#     #if not app_loader2.started:
#         t = threading.Thread(target=apps.start_up()).setDaemon(True).start()
#         print 'In views ... App Started !!!!!!'
#     return


def acxis_login(request):
    glm_domain =     'https://glm-beta.herokuapp.com'
    client_id='a0f7f526b1381551f2e0e9c8ca3d312cf93134ce5afbd234c9b6b53e5a257a97'
    client_secret = '5fe8feaff0c477b05462bf08f40a868f1a28972d9280a1f0a7de7cdddb84701e'
    redirect = 'http://10.0.51.101:8003/acxis/callback'

    init_ip = list()

    bypass_employee_login = request.GET.get('bypass', None)
    if bypass_employee_login:
        log.debug('bypass_employee_login == ' +  bypass_employee_login)
    # Determine IP address of the user. If nternal subnet than present internal A10 Employee
    #  login template. If not, present customer login template
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print ip

    if ip:
        init_ip = ip.split('.')[0]
        print init_ip

    if bypass_employee_login is None and init_ip in ["172", "10", "192", "127"]:
            # al10_login.html will make POST call to a10_login_post
            if request.user.is_authenticated():
                url = reverse('global_index')
                return HttpResponseRedirect(url)
            else:
                return render(request, "a10_login.html", {})

    redirect_url = glm_domain + '/oauth/authorize?response_type=code'
    redirect_url += '&client_id=' + client_id
    redirect_url += '&client_secret=' + client_secret
    redirect_url += '&redirect_uri=' + redirect
    log.debug('redirect_url === ' + redirect_url)
    return  HttpResponseRedirect(redirect_url)

@csrf_exempt
def employee_login(request):
    # For A10 Employee login
    # For A10 Employee  - For tiial, to be deleted
    if request.user.is_authenticated():
        print 'user already authenticated $$$$'
        url = reverse('global_index', current_app=True)
        return HttpResponseRedirect(url)

    employee_user = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            try:
                ldap_auth = MyLDAPBackend()
                employee_user = ldap_auth.authenticate(request, username=username, password=password)
            except Exception, es:
                print es

            if employee_user:
                employee_user.backend = 'django_auth_ldap.backend.LDAPBackend'
                print employee_user
                # calling super class login method
                login(request, employee_user)
                request.session['account_type'] = "employee"
            else:
                url = reverse('acxis_login')
                return HttpResponseRedirect(url)
        except ldap.LDAPError, re:
            print re
            #employee_user = ModelBackend.authenticate(username, password)
            #employee_user.backend = 'django.contrib.auth.backends.ModelBackend'
            url = reverse('acxis_login')
            return HttpResponseRedirect(url)
        finally:
            ldap_auth = None

        #print employee_user.is_authenticated()

        url = reverse('global_index')
        return HttpResponseRedirect(url)

    url = reverse('acxis_login')
    return HttpResponseRedirect(url)


@csrf_exempt
def acxis_callback(request):
    """
    call back is used by GLM to authenticate customers.
    GLM must pass:
    email
    username
    First and Last name
    CustomerID
    Customer Name
    in request callback. Upon receiving the callback, we create a user in ACXIS for the customer profile
    :param request:
    :return:
    """
    glm_domain = 'https://glm-beta.herokuapp.com'
    client_id='a0f7f526b1381551f2e0e9c8ca3d312cf93134ce5afbd234c9b6b53e5a257a97'
    client_secret = '5fe8feaff0c477b05462bf08f40a868f1a28972d9280a1f0a7de7cdddb84701e'
    redirect = 'http://10.0.51.101:8003/acxis/callback'

    log.debug('in Callback method')

    if request.method == "POST":
        log.debug('in Callback method POST method')
        access_token = request.POST.get('token', None)
        print 'access_token ==> ', access_token
        customer_id = request.POST.get('customer_id', '')
        print 'callback =====> ', customer_id

        if customer_id and customer_id != 'None':
            url = reverse('customer_index', kwargs={'customer_id': customer_id}, current_app=True)
            print url
            return HttpResponseRedirect(url)
    if request.method == "GET":

        # Using Auth Token, get the access token
        log.debug('in Callback method GET method')
        authorization_code = request.GET.get('code', None)
        log.debug('authorization_code ===' + authorization_code)

        # param_data = {
        #     'grant_type':  'authorization_code',
        #     'code': authorization_code,
        #     'client_id': client_id,
        #     'client_secret': client_secret,
        #     'redirect_uri': redirect
        # }

        rest_url = glm_domain + '/oauth/token'
        rest_url +=  '?grant_type=authorization_code'
        rest_url += '&client_id=' + client_id
        rest_url += '&client_secret=' + client_secret
        rest_url += '&code=' + authorization_code
        rest_url += '&redirect_uri=' + redirect

        log.debug('token request ==' +  rest_url)
        resp = requests.post(url=rest_url)
        log.debug(resp)
        data = json.loads(resp.text)
        access_token = data['access_token']
        log.debug('token === ' + access_token)
        expires_in = data['expires_in']
        created_at = data['created_at']
        log.debug('expires_in === ' + str(expires_in) + " created_at == " + str(created_at))


        # Get User information from GLM
        log.debug('========= Getting User Information ==============')
        glm_user_profile_url = glm_domain + '/users/me.json'
        headers={
            "Authorization": 'Bearer ' + access_token
        }
        profile_response = requests.get(glm_user_profile_url, headers=headers)
        log.debug(profile_response)
        profile_data = json.loads(profile_response.text)
        log.debug(profile_data)
        # Persist GLM Customer information and access_token and time stamp
        request.session['account_type'] = "customer"

        # Redirect user to ACXIS Portal
        acxis_url = reverse('redirect_customer', kwargs={'customer_id': '0016000000G8UcB'}, current_app=True)
        return HttpResponseRedirect(acxis_url)



class MyLDAPBackend(LDAPBackend):
    """ A custom LDAP authentication backend for A10 Empoyee login there by creating a user in ACXIS """

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        """ Overrides LDAPBackend.authenticate to save user password in django """
        user = None
        try:
            print '1111111'
            user = LDAPBackend.authenticate(self, request, username, password)
            print user
            #print self.user.cn

            # If user has successfully logged, save his password in django database
            #if user:
                   # user.set_password(password)
                #user.save()
        except Exception,  e:
            print e

        return user

    def get_or_create_user(self, username, ldap_user):
        print 'in get or create '
        """ Overrides LDAPBackend.get_or_create_user to force from_ldap to True """

        kwargs = {
            'username': username,
        }

        return User.objects.get_or_create(**kwargs)