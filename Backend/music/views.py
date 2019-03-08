from typing import Dict, Any
from .models import Album
# from django.template import loader
from django.shortcuts import render, get_object_or_404
# Create your views here.

def index(request):
    all_albums = Album.objects.all()
    context ={'all_albums': all_albums}
    return render(request, 'music/index.html', context)


def detail(request, album_id):

    album = get_object_or_404(Album , pk=album_id)
    return render(request, 'music/details.html', {'album': album})
