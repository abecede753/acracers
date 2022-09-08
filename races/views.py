from django.views.generic import DetailView
from races.models import RaceSetup


class RaceSetupDetailView(DetailView):

    model = RaceSetup

    def XXXget_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['book_list'] = RaceSetup.objects.all()
        return context
