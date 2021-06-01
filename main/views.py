# from django.shortcuts import redirect
from steamauth import auth, get_uid
from django.http import HttpResponse


def login(request):
    return auth('/roulette/callback/')


def login_callback(request):
    steam_uid = get_uid(request.GET)
    if steam_uid is None:
        return HttpResponse('error')
    else:
        return HttpResponse('ok')
