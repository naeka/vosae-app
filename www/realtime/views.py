# -*- Coding:Utf-8 -*-

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json

from realtime.utils import PUSHER_IS_CONFIGURED, pusher


@csrf_exempt
@require_GET
def pusher_auth(request):
    channel = request.GET["channel_name"]
    socket_id = request.GET["socket_id"]

    if PUSHER_IS_CONFIGURED and request.user.is_authenticated():
        r = pusher[channel].authenticate(socket_id)
        return HttpResponse('{0}({1})'.format(request.GET["callback"], json.dumps(r)), mimetype="application/javascript")
    return HttpResponseForbidden("Not Authorized")
