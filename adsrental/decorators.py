import base64
from functools import wraps
import typing

from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views import View


def view_or_basicauth(view: typing.Callable, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
    # Check for valid basic auth header
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1].encode()).decode().split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active:
                    request.user = user
                    return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % settings.BASIC_AUTH_REALM
    return response


def basicauth_required(view_func: typing.Callable) -> HttpResponse:
    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        return view_or_basicauth(view_func, request, *args, **kwargs)
    return wrapper


def https_required(function: typing.Callable) -> HttpResponse:
    def wrap(self: View, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        protocol = 'http'
        if request.is_secure():
            protocol = 'https'

        actual_domain = '{}://{}'.format(protocol, request.get_host())
        if actual_domain == settings.DOMAIN or not settings.CHECK_DOMAIN:
            return function(self, request, *args, **kwargs)

        url = u'{host}{path}'.format(
            host=settings.DOMAIN,
            path=request.get_full_path()
        )
        return HttpResponseRedirect(url)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
