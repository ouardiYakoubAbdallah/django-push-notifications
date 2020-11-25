from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from webpush import send_user_notification

import json


@require_GET
def home(request):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user
    return render(
        request=request,
        template_name='home.html',
        context={
            user: user,
            'vapid_key': vapid_key
        }
    )


@require_POST
@csrf_exempt
def send_push(request):
    """
    This view gets the body of the request and deserializes the JSON document to a Python object.
    The view expects the request body object to have three properties:
        head: The title of the push notification.
        body: The body of the notification.
        id: The id of the request user.
    """
    try:
        body = request.body
        data = json.loads(body)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(
                status=400,
                data={
                    'message': 'Invalid data format'
                }
            )

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {
            'head': data['head'],
            'body': data['body']
        }
        send_user_notification(user=user, payload=payload, ttl=1000)
        return JsonResponse(
            status=200,
            data={
                'message': 'Push notification sent !'
            }
        )

    except TypeError as ex:
        return JsonResponse(
            status=500,
            data={
                'message': 'Invalid data format',
                'error': str(ex)
            }
        )