from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from rest_framework import viewsets

from .models import Task
from .permissions import IsOwner
from .serializers import TaskSerializer


def home_view(request):
    if request.user.is_authenticated:
        todo = sorted(list(request.user.tasks.filter(complete=False).values('id', 'title', 'complete', 'modified')),
                      key=lambda x: x['modified'])[::-1]
        complete = sorted(list(request.user.tasks.filter(complete=True).values('id', 'title', 'complete', 'modified')),
                          key=lambda x: x['modified'])[::-1]
        return render(request, 'home.html', context={'todo': todo, 'complete': complete})
    return render(request, 'home.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Złe hasło lub nazwa użytkownika.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Wylogowano pomyślnie.')
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.info(request, "Rejestracja przebiegła pomyślnie")
            return redirect('home')
        else:
            return render(request, 'register.html', context={'form': form})

    form = UserCreationForm(request)
    return render(request, 'register.html', context={'form': form})


class TasksViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    def get_queryset(self, *args, **kwargs):
        return Task.objects.all().filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
