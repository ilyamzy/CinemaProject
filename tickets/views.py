from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


from cinema_sessions.models import CinemaSession
from halls.models import Hall, Seat
from .models import Ticket


class TicketsChoiseView(View):
    def get(self, request, hall_id, session_id):
        hall = get_object_or_404(Hall, pk=hall_id)
        session = get_object_or_404(CinemaSession, pk=session_id)
        seats = Seat.objects.filter(hall=hall)
        seats_dict = {
            f'{seat.row},{seat.col}': {
                'id': seat.id,
                'type': seat.seat_type,
            }
            for seat in seats
        }

        reserved_seat_ids = set()
        if session_id:
            tickets = Ticket.objects.filter(session_id=session_id).filter(
                Q(is_reserved=True) | Q(is_paid=True)
            )
            reserved_seat_ids = set(tickets.values_list('seat_id', flat=True))

        context = {
            'hall': hall,
            'seats_dict': seats_dict,
            'rows': hall.rows,
            'cols': hall.cols,
            'reserved_seat_ids': reserved_seat_ids,
            'session_id': session_id,
            'start_time': session.start_time,
            'single_seat_price': session.single_seat_price,
            'double_seat_price': session.double_seat_price,
        }
        return render(request, 'tickets/tickets_choice.html', context)

    def post(self, request, hall_id, session_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Войдите в аккаунт, чтобы забронировать билеты.')
            return redirect('login')

        selected_seats = request.POST.get('selected_seats', '')
        if not selected_seats:
            messages.error(request, 'Не выбрано ни одного места.')
            return redirect(request.path)

        seat_ids = selected_seats.split(',')
        session = get_object_or_404(CinemaSession, pk=session_id)

        tickets_to_reserve = Ticket.objects.filter(
            session=session,
            seat_id__in=seat_ids,
            is_reserved=False
        )

        if tickets_to_reserve.count() != len(seat_ids):
            messages.error(request, 'Некоторые выбранные места уже заняты.')
            return redirect(request.path)

        tickets_to_reserve.update(
            user=request.user,
            is_reserved=True,
            is_paid=False
        )

        messages.success(request, 'Места успешно забронированы.')
        return redirect('my_tickets')


class MyTicketsView(LoginRequiredMixin, TemplateView):
    template_name = 'tickets/my_tickets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        tickets = self.request.user.tickets.select_related('session', 'seat').all()

        context['booked'] = tickets.filter(is_reserved=True, is_paid=False, session__start_time__gt=now)
        context['active'] = tickets.filter(is_paid=True, session__start_time__gt=now)
        context['expired'] = tickets.filter(session__start_time__lte=now)
        return context


class PayTicketView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)

        if ticket.is_reserved and not ticket.is_paid:
            ticket.is_paid = True
            ticket.is_reserved = False
            ticket.save()
            messages.success(request, 'Билет успешно оплачен.')
        else:
            messages.error(request, 'Этот билет нельзя оплатить.')

        return redirect('my_tickets')
