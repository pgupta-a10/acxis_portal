from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.encoding import smart_unicode
import datetime
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.contenttypes.models import ContentType


def get_content_type(obj):
    """Returns the ContentType of the object"""
    try:
        return ContentType.objects.get_for_model(obj)
    except:
        return ContentType.objects.none()


def strip_html_tags(text):
    tmp = text
    tmp = strip_tags(tmp)
    return tmp


def strip_html(text):
    tmp = text
    tmp = strip_tags(tmp)
    #tmp = strip_entities(tmp)
    return tmp


def strip_whitespace(data):
    """Strips HTML tags and entities from the data. Then strips carriage return, new lines, and tabs.
    Returns the remaining data string."""
    tmp = data
    tmp = strip_tags(tmp)
    #tmp = strip_entities(tmp)
    tmp = tmp.strip(' \t\n\r')
    return tmp


def get_utc_from_local_datetime(dt):
    """Takes local naive datetime object and converts it to UTC"""
    tz = timezone.get_default_timezone()
    local_dt = timezone.make_aware(dt, tz)
    utc_dt = datetime.datetime.astimezone(local_dt, timezone.utc)
    return utc_dt


def get_local_from_utc_datetime(dt):
    """Reverse of get_utc_from_local_datetime"""
    tz = timezone.get_default_timezone()
    utc_dt = timezone.make_aware(dt, timezone.utc)
    local_dt = datetime.datetime.astimezone(utc_dt, tz)
    return local_dt


def get_mysql_string_from_datetime(dt, convert_utc=False):
    """Takes a Python datetime object and returns a String representation that can be used in MySQL queries.
    Optional: set 'covert_utc' argument to True to convert the local naive datetime object into UTC datetime first.
    """
    if convert_utc:
        dt = get_utc_from_local_datetime(dt)
    return datetime.datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")


def clean_windows_enc_string(s):
    """Users smart_unicode to cleanup Windows encoding in strings (note: primarily used for short_desc in Bugzilla)"""
    try:
        cleaned = smart_unicode(s, encoding='windows-1252', strings_only=False, errors='strict')
        return cleaned
    except Exception, e:
        pass

    try:
        cleaned = smart_unicode(s, encoding='utf-8', strings_only=False, errors='strict')
        return cleaned
    except Exception, e:
        return ""
    return ""


def strip_non_ascii(string):
    """Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)


def strip_non_ascii_dict(data):
    """
    Takes a dictionary and strips all non-ascii characters from each key's value if it is a string or unicode string
    """
    cleaned_data = {}
    for k in data.keys():
        if isinstance(data[k], str) or isinstance(data[k], unicode):
            temp = strip_non_ascii(data[k])
            if len(strip_whitespace(temp)):
                cleaned_data[k] = temp
            else:
                cleaned_data[k] = ""
        else:
            cleaned_data[k] = data[k]
    return cleaned_data
