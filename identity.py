from django.http import HttpResponseBadRequest
from django.conf import settings

from hashlib import sha256, md5
from urllib import quote

def identity_required(func):
    def inner(request, *args, **kwargs):
        user = request.GET.get('user', None)
        param_hash = request.GET.get('hash', None)
        course = request.GET.get('course', None)
        rich_url = request.GET.get('UrlDynamicCreatedBy', None) is not None
        secret = settings.AUTHENTICATION_SECRET

        if user and course and param_hash:
            if rich_url:
                paramlist = request.GET.get('paramlist', "")
                hash_contents = []
                for param in paramlist.split(","):
                    if param == "pw":
                        hash_contents.append(secret)
                    else:
                        hash_contents.append(request.GET.get(param, ""))
                hash_string = (md5(",".join(hash_contents)).
                         hexdigest().upper())
            else:
                timestamp = request.GET.get('timestamp', None)
                hash_contents = [user, timestamp, course, secret]
                hash_string = (sha256(",".join(hash_contents)).
                        hexdigest().upper())

            if hash_string == param_hash.upper():
                request.authenticated_course = course
                request.authenticated_user = user
                request.session['authenticated_course'] = course
                request.session['authenticated_user'] = user
            else:
                return HttpResponseBadRequest((
                    'Provided hash is incorrect.\n'
                    "%s !== %s %s" % (hash_string, param_hash.upper(),
                        hash_contents)))

        if ('authenticated_course' in request.session and
                'authenticated_user' in request.session):
            request.signed_url_params = generate_signed_params(
               request.session.get("authenticated_user"),
               request.session.get("authenticated_course"))
            request.signed_url_params_unquoted = generate_signed_params(
               request.session.get("authenticated_user"),
               request.session.get("authenticated_course"), quoted=False)
            return func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest('No authentication.')

    return inner

def generate_signed_params(user, course, timestamp=None, quoted=True):
    from time import time
    from urllib import quote
    timestamp = timestamp or str(int(time()))
    secret = settings.AUTHENTICATION_SECRET
    hash_string = (sha256(",".join([user, str(timestamp), course, secret])).
            hexdigest().upper())
    if quoted:
        course = quote(course, '')
    return "user=%s&timestamp=%s&course=%s&hash=%s" % (
            user, timestamp, course, hash_string)
