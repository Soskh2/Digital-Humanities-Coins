from django.shortcuts import render

# Create your views here.

# Home page/default
def index(request):
    return render(request, "coins/index.html", {})

def coin_data(request):
    return render(request, "coins/coin_data.html", {})