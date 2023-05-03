from django.shortcuts import render
from django.http import JsonResponse
from .utils import get_images, get_coin, form_filter, get_info

# Create your views here.

# Home page/default
def index(request):
    filter = ''
    if request.method == "POST":
        filter = form_filter(request.POST)
    # In utils.py, array of images where each image contains image link and name
    images, origins, materials = get_images(filter)
    return render(request, "coins/index.html", {"images": images, "origins": origins, "materials": materials})

# After user clicks on a coin
def coin_data(request):
    qid = request.GET.get("id")
    in_arabic = False
    labels = ["Description", "Location of Creation", "Time Period", "Inception", "Made From Material", "Die Axis", "Diameter", "Mass", "Inventory Number", "Wikidata Q identifier"]
    if "in_arabic" in request.GET and request.GET.get("in_arabic") == "true":
        in_arabic = True
        # NOTE: DIE AXIS WAS THE ONLY LABEL WITHOUT A TRANSLATION ON WIKIDATA, SO THIS TEMPORARILY USES A GOOGLE TRANSLATION
        labels = ["الوصف", "موقع التجميع النهائي", "الفترة الزمنية", "البداية", "المواد المستخدمة", "محور يموت", "القطر", "الكتلة", "مُعرِّف الجَرد", "معرف ويكي بيانات"]
    data = get_coin(qid, in_arabic)
    data.append(qid)
    return render(request, "coins/coin_data.html", {"data": data, "labels":labels, "in_arabic":(True if in_arabic else False)})

def cabinet_view(request):
    coin_info = request.GET.get("this")
    if (coin_info):
        data = get_info(coin_info)
        print(data)
        return JsonResponse({"data": data})
    return render(request, "coins/Cabinet-view.html")