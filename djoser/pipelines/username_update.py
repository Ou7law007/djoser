from django.contrib.auth import get_user_model

from djoser import exceptions, signals
from djoser.conf import settings
from djoser.pipelines.base import BasePipeline

User = get_user_model()


def serialize_request(request, context):
    if settings.SET_USERNAME_RETYPE:
        serializer_class = settings.SERIALIZERS.set_username_retype
    else:
        serializer_class = settings.SERIALIZERS.set_username
    serializer = serializer_class(data=request.data, **{'context': context})
    if not serializer.is_valid(raise_exception=False):
        raise exceptions.ValidationError(serializer.errors)
    return {'serializer': serializer}


def perform(request, context):
    assert 'serializer' in context

    user = request.user
    new_username = context['serializer'].validated_data[User.USERNAME_FIELD]
    setattr(user, User.USERNAME_FIELD, new_username)
    user.save(update_fields=[User.USERNAME_FIELD])

    return {'user': user}


def signal(request, context):
    assert context['user']
    user = context['user']

    signals.username_updated.send(sender=None, user=user, request=request)


class Pipeline(BasePipeline):
    steps = settings.PIPELINES.username_update