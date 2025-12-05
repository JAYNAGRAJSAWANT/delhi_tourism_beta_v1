# decorators.py
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

from .jwt_utils import decode_access_token


def admin_jwt_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        token = request.COOKIES.get("admin_access_token")
        if not token:
            return HttpResponseRedirect(reverse("admin_login"))

        user, error = decode_access_token(token)
        if error or not user or not user.is_staff:
            response = HttpResponseRedirect(reverse("admin_login"))
            response.delete_cookie("admin_access_token")
            return response

        # attach authenticated user to request
        request.user = user
        return view_func(request, *args, **kwargs)

    return _wrapped
