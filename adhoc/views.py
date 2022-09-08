import psutil
import subprocess

from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from adhoc.models import AdhocRace
from races.models import RaceSetup


class AdhocCreateView(UserPassesTestMixin, CreateView):
    model = AdhocRace
    fields = ('racesetup', 'practice_minutes', 'qualifying_minutes',
              'race_minutes', 'reverse_grid', 'join_password',
              'admin_password', 'fixed_setups', 'show_public',
              'start_rule')
    login_url = '/'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['racesetups'] = RaceSetup.objects.exclude(
            hidden=True).order_by("title")
        return context

    def get_success_url(self):
        return reverse_lazy('home')

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        props = self.request.user.props
        initial['practice_minutes'] = props.practice_minutes
        initial['qualifying_minutes'] = props.qualifying_minutes
        initial['race_minutes'] = props.race_minutes
        initial['reverse_grid'] = props.reverse_grid
        initial['join_password'] = props.join_password
        initial['admin_password'] = props.admin_password
        initial['fixed_setups'] = props.fixed_setups
        initial['show_public'] = props.show_public
        initial['start_rule'] = props.start_rule
        return initial


class AdhocDeleteView(DeleteView):
    model = AdhocRace
    success_url = reverse_lazy('home')


class AdhocKill(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        for x in psutil.process_iter():
            if x.name() == 'acServer':
                subprocess.Popen.kill(x)
        return HttpResponse("OK")

