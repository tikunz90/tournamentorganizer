from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy

from beachhandball_app.static_views import getContext
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView

from ..models.Tournament import Court, Tournament
from beachhandball_app.forms.basic_setup.forms import CourtForm, CourtUpdateForm


class CourtCreateView(LoginRequiredMixin, UserPassesTestMixin, BSModalCreateView):
    template_name = 'beachhandball/templates/create_form.html'
    form_class = CourtForm
    success_message = 'Success: Court was created.'

    def get_context_data(self, **kwargs):
        context = super(CourtCreateView, self).get_context_data(**kwargs)
        user_context = getContext(self.request)
        context['form'].fields['tournament'].queryset = Tournament.objects.filter(organizer=user_context['gbo_user'].subject_id)
        return context
    
    def get_success_url(self):
        return reverse("basic_setup")

    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()


class CourtDeleteView(LoginRequiredMixin, UserPassesTestMixin, BSModalDeleteView):
    model = Court
    template_name = 'beachhandball/tournamentevent/delete_state.html'
    success_message = 'Success: Court was deleted.'

    def get_success_url(self):
        return reverse("basic_setup")

    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()


class CourtUpdateView(LoginRequiredMixin, UserPassesTestMixin, BSModalUpdateView):
    model = Court
    template_name = 'beachhandball/templates/update_form.html'
    form_class = CourtUpdateForm
    success_message = 'Success: Court was updated.'

    def get_success_url(self):
        return reverse("basic_setup")

    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()
