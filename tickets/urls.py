from django.urls import path


from .views import TicketsChoiseView, MyTicketsView, PayTicketView


urlpatterns = [
    path('choice/<int:hall_id>/<int:session_id>/', TicketsChoiseView.as_view(), name='tickets_choice'),
    path('my-tickets/', MyTicketsView.as_view(), name='my_tickets'),
    path('pay-ticket/<int:ticket_id>/', PayTicketView.as_view(), name='pay_ticket'),
]
