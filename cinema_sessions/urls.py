from django.urls import path


from .views import CinemaSessionAddView, AfishaView, FilmSessionsDateView


urlpatterns = [
    path('add/', CinemaSessionAddView.as_view(), name='session_add'),
    path('afisha/', AfishaView.as_view(), name='afisha'),
    path('filmsessions/', FilmSessionsDateView.as_view(), name='film_sessions'),
]
