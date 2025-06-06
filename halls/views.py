from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from .serializers import HallCreateSerializer
from .models import Hall, Seat


class HallCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        return render(request, 'halls/hall_create.html')

    def test_func(self):
        return self.request.user.role == 'manager' or self.request.user.role == 'admin'


class HallSaveView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request):
        try:
            serializer = HallCreateSerializer(data=request.POST, files=request.FILES)
            if not serializer.is_valid():
                return JsonResponse({'errors': serializer.errors}, status=400)

            data = serializer.validated_data

            with transaction.atomic():
                hall = Hall.objects.create(
                    name=data['name'],
                    rows=data['rows'],
                    cols=data['cols'],
                )

                if data["poster"]:
                    hall.poster.save(data["poster"].name, data["poster"], save=True)

                seat_objs = [
                    Seat(
                        hall=hall,
                        row=seat["row"],
                        col=seat["col"],
                        seat_type=seat["seat_type"]
                    )
                    for seat in data["seats"]
                ]
                Seat.objects.bulk_create(seat_objs)

            return JsonResponse({'message': 'Hall and seats created successfully', 'id': hall.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def test_func(self):
        return self.request.user.role in ('manager', 'admin')



class AllHallsView(ListView):
    model = Hall
    template_name = 'halls/all_halls.html'
    context_object_name = 'all_halls'


class HallDetailView(View):
    def get(self, request, pk):
        hall = get_object_or_404(Hall, pk=pk)
        seats = Seat.objects.filter(hall=hall)

        seat_map = {}
        for seat in seats:
            seat_map[f'{seat.row},{seat.col}'] = seat.seat_type
        context = {
            'hall': hall,
            'seat_map': seat_map,
            'rows': hall.rows,
            'cols': hall.cols,
        }
        return render(request, 'halls/hall_details.html', context)


class DeleteHallView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'manager' or self.request.user.role == 'admin'

    def post(self, request, pk):
        try:
            movie = Hall.objects.get(pk=pk)
            movie.delete()
            return JsonResponse({'success': True}, status=200)
        except Hall.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Movie not found'}, status=404)