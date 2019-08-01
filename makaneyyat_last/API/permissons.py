import typing

from django.conf import settings
from rest_framework import permissions

from rest_framework_api_key.models import APIKey

class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'list':
            return _check_permissions_action(request)
        elif view.action == 'create':
            return request.user.is_authenticated()
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated():
            return False

        if view.action == 'retrieve':
            return obj == request.user or request.user.is_authenticated
        elif view.action in ['update', 'partial_update']:
            return False
        elif view.action == 'destroy':
            return False
        else:
            return False


def _get_key(request) -> typing.Optional[str]:
    custom_header = getattr(settings, "API_KEY_CUSTOM_HEADER", None)

    if custom_header is not None:
        return _get_key_from_custom_header(request, custom_header)

    return _get_key_from_authorization(request)


def _get_key_from_authorization(request) -> typing.Optional[str]:
    authorization = request.META.get("HTTP_AUTHORIZATION")

    if not authorization:
        return None

    try:
        _, key = authorization.split("Api-Key ")
    except ValueError:
        key = None

    return key


def _get_key_from_custom_header(request, name: str) -> typing.Optional[str]:
    header = request.META.get(name)
    return header if header else None

def _check_permissions_action(request):
    key = _get_key(request)

    has_key = False
    if key:
        has_key = APIKey.objects.is_valid(key)

    return request.user.is_authenticated() or has_key

