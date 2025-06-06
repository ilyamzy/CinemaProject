from django import forms


from .models import Movie


class MovieAddForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'country', 'genre', 'duration', 'budget', 'poster', 'description', 'rating', 'release_date']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
            'genre': forms.SelectMultiple(attrs={'id': 'genre-select'}),
        }


class MovieEditForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['release_date'].input_formats = ['%Y-%m-%d']
