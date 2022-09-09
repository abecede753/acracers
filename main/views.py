from steam.webapi import WebAPI
from steamauth import auth, get_uid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from main.models import Props
from adhoc.models import AdhocRace, cleanup_AdhocRace_indices


class Home(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        cleanup_AdhocRace_indices()
        context = super().get_context_data(**kwargs)
        rq = AdhocRace.objects.filter(index__gt=0).order_by("index")
        context['queue'] = rq
        current = AdhocRace.objects.filter(
            start_ts__isnull=False, end_ts__isnull=True,
            index__isnull=True)
        if current.count():
            context['current'] = current[0]
        else:
            context['current'] = None
        context['joinurl'] = ('acmanager://race/online/join?'
                              'ip={0}&httpPort={1}').format(
                                  settings.ACSERVERWRAPPERIP,
                                  settings.ACSERVERPORT)
        return context


class HomeUpdate(Home):
    template_name = 'main/home_update.html'


def steamlogin(request):
    return auth('/steamlogin/callback/')


def _userinfo(steam_uid):
    api = WebAPI(settings.STEAM_WEB_API)
    fullinfo = api.ISteamUser.GetPlayerSummaries(steamids=steam_uid)
    return fullinfo['response']['players'][0]


def steamlogin_callback(request):
    steam_uid = get_uid(request.GET)
    if steam_uid is None:
        return HttpResponse('error')

    user, created = User.objects.get_or_create(
        username='{0}'.format(steam_uid))
    if created:
        user.save()
        userinfo = _userinfo(steam_uid)
        props = Props(user=user)
        props.personaname = userinfo['personaname']
        props.icon = userinfo['avatar']
        props.save()
        user.first_name = userinfo['personaname']
        user.save()

    login(request, user)
    return redirect('home')


class PropsUpdateView(UpdateView):
    model = Props
    fields = ('practice_minutes', 'qualifying_minutes',
              'race_minutes', 'reverse_grid', 'join_password',
              'admin_password', 'fixed_setups', 'show_public',
              'start_rule')

    def get_success_url(self):
        return reverse_lazy('home')
