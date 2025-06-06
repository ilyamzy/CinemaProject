import json


from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from serializers_pkg import serializers

from .models import Movie, Genre
from .forms import MovieAddForm, MovieEditForm


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie.html'
    context_object_name = 'movie'


class MovieCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Movie
    form_class = MovieAddForm
    template_name = 'movies/movie_add.html'

    def test_func(self):
        return self.request.user.role == 'manager' or self.request.user.role == 'admin'

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        print(next_url)
        if next_url:
            return next_url
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        genres_str = self.request.POST.get('genres')
        if genres_str:
            genre_ids = [int(pk) for pk in genres_str.split(',') if pk.isdigit()]
            self.object.genres.set(genre_ids)
        return response

    def form_invalid(self, form):
        print("FORM ERRORS:", form.errors)
        return super().form_invalid(form)


@method_decorator(require_POST, name='dispatch')
class AddGenreView(View):
    def post(self, request, *args, **kwargs):

        serializer = serializers.GenreSerializer(data=request.body)
        if not serializer.is_valid():
            return JsonResponse({'success': False, 'errors': serializer.errors}, status=400)

        genre, created = Genre.objects.get_or_create(name=serializer.validated_data['name'])
        return JsonResponse({'success': True, 'id': genre.id})


class AllMoviesView(ListView):
    model = Movie
    template_name = 'movies/all_movies.html'
    context_object_name = 'all_movies'


class DeleteMovieView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'manager' or self.request.user.role == 'admin'

    def post(self, request, pk):
        try:
            movie = Movie.objects.get(pk=pk)
            movie.delete()
            return JsonResponse({'success': True})
        except Movie.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)


class EditMovieInfoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Movie
    form_class = MovieEditForm
    template_name = 'movies/movie_edit.html'
    extra_context = {
        'title': "Редактирование информации",
    }

    def test_func(self):
        return self.request.user.role == 'manager' or self.request.user.role == 'admin'

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        print(next_url)
        if next_url:
            return next_url
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['selected_genres'] = [genre.id for genre in self.object.genre.all()]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        genres_str = self.request.POST.get('genres')
        if genres_str:
            genre_ids = [int(pk) for pk in self.request.POST.getlist('genre')]
            self.object.genre.set(genre_ids)
        return response

    def form_invalid(self, form):
        print("FORM ERRORS:", form.errors)
        return super().form_invalid(form)
