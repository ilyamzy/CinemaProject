from django.urls import path


from .views import HallCreateView, HallSaveView, AllHallsView, HallDetailView, DeleteHallView


urlpatterns = [
    path('create/', HallCreateView.as_view(), name='hall_create'),
    path('save/', HallSaveView.as_view(), name='hall_save'),
    path('', AllHallsView.as_view(), name='all_halls'),
    path('<int:pk>/', HallDetailView.as_view(), name='hall_details'),
    path('<int:pk>/delete/', DeleteHallView.as_view(), name='delete_hall'),
]
