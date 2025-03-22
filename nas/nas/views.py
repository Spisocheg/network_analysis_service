from django.shortcuts import render


def index(request):
    return render(request, 'nas_index.html')
