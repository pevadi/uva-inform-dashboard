from django.http import HttpResponseBadRequest
from django.conf import settings

from hashlib import sha256

def identity_required(func):
    def inner(request, *args, **kwargs):
        # Fetch email from GET paramaters if present and store in session.
        user = request.GET.get('user', None)
        course = request.GET.get('course', None)
        timestamp = request.GET.get('timestamp', None)
        param_hash = request.GET.get('hash', None)
        if param_hash is not None:
            secret = settings.AUTHENTICATION_SECRET
            hash_contents = [user, timestamp, course, secret]
            hash_string = sha256(",".join(hash_contents)).hexdigest().upper()
            if hash_string == param_hash.upper() and user is not None and user != "":
                request.session['user'] = user
                request.session['course'] = course

        # Fetch user from session
        user = request.session.get('user', None)

        if user is None:
            return HttpResponseBadRequest()
        else:
            request.signed_url_params = generate_signed_params(
                request.session.get("user"),
                request.session.get("course"))
            return func(request, *args, **kwargs)
    return inner

def generate_signed_params(user, course):
    from time import time
    from urllib import quote
    timestamp = str(int(time()))
    secret = settings.AUTHENTICATION_SECRET
    hash_string = (sha256(",".join([user,str(timestamp), course, secret])).
            hexdigest().upper())
    return "user=%s&timestamp=%s&course=%s&hash=%s" % (
            user, timestamp, quote(course, ''), hash_string)
