from django.shortcuts import render
from .utils import get_coin_images

# Create your views here.

# Home page/default
def index(request):
    images = get_coin_images()
    return render(request, "coins/index.html", {"images": images})

def coin_data(request):
    return render(request, "coins/coin_data.html", {})