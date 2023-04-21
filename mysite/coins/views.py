from django.shortcuts import render
from .utils import get_default_images, get_coin

# Create your views here.

# Home page/default
def index(request):
    # In utils.py, array of images where each image contains image link and name
    images, origins = get_default_images()
    origins = list(origins)
    origins.sort()
    return render(request, "coins/index.html", {"images": images, "origins": origins})

# After user clicks on a coin
def coin_data(request):
    qid = request.GET.get("id")
    data = get_coin(qid)
    data.append(qid)
    return render(request, "coins/coin_data.html", {"data": data})