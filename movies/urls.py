from django.urls import path


from .views import (MovieDetailView, MovieCreateView, AddGenreView,
                    AllMoviesView, DeleteMovieView, EditMovieInfoView)


urlpatterns = [
    path('add/', MovieCreateView.as_view(), name='movie_add'),
    path('', AllMoviesView.as_view(), name='all_movies'),
    path('<int:pk>/delete/', DeleteMovieView.as_view(), name='delete_movie'),
    path('edit/<int:pk>', EditMovieInfoView.as_view(), name='edit_movie'),
    path('<int:pk>/', MovieDetailView.as_view(), name='movie_details'),
    path('genre/add/', AddGenreView.as_view(), name='add_genre'),
]
