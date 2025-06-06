from datetime import datetime


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.utils import timezone
from django.db.models import Prefetch


from movies.models import Movie
from halls.models import Hall
from tickets.models import Ticket
from .models import CinemaSession
from .forms import CinemaSessionAddForm


class CinemaSessionAddView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CinemaSession
    form_class = CinemaSessionAddForm
    template_name = 'cinema_sessions/cinema_session_add.html'

    def test_func(self):
        return self.request.user.role in ['manager', 'admin']

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

    def form_valid(self, form):
        form.instance.start_time = form.cleaned_data['start_time']
        response = super().form_valid(form)

        session = self.object
        seats = session.hall.seats.all()

        tickets = []
        for seat in seats:
            price = (
                session.single_seat_price
                if seat.seat_type == 'single'
                else session.double_seat_price
            )
            tickets.append(Ticket(session=session, seat=seat, price=price))
        Ticket.objects.bulk_create(tickets)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = Movie.objects.all()
        context['halls'] = Hall.objects.all()
        return context


class AfishaView(ListView):
    model = Movie
    template_name = 'cinema_sessions/afisha.html'
    context_object_name = 'movies_with_sessions'

    def get_queryset(self):
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        sessions = CinemaSession.objects.filter(
            start_time__date=selected_date
        ).select_related('movie', 'hall')

        return Movie.objects.filter(sessions__in=sessions).distinct().prefetch_related(
            Prefetch('sessions', queryset=sessions)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        context['selected_date'] = selected_date
        context['selected_date_str'] = selected_date.isoformat()
        context['min_date'] = timezone.now().date().isoformat()
        return context


class FilmSessionsDateView(ListView):
    model = CinemaSession
    template_name = 'cinema_sessions/get_sessions.html'
    context_object_name = 'film_sessions_date'

    def get_queryset(self):
        self.date_str = self.request.GET.get('date')
        self.movie_id = self.request.GET.get('movie_id')

        if self.date_str:
            try:
                self.selected_date = datetime.strptime(self.date_str, '%Y-%m-%d').date()
            except ValueError:
                self.selected_date = timezone.now().date()
        else:
            self.selected_date = timezone.now().date()

        return CinemaSession.objects.filter(
            start_time__date=self.selected_date,
            movie=self.movie_id
        ).select_related('hall', 'movie')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.selected_date
        context['film'] = get_object_or_404(Movie, id=self.movie_id)
        return context
