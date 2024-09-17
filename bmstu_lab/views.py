from django.shortcuts import render
from django.http import HttpResponse

ADDRESSES = [{"address": "141151, Липецкая область, город Кашира, пл. 1905 года, 06", "id": 1}, 
             {"address": "828181, Омская область, город Одинцово, пер. Домодедовская, 13", "id": 2},
             {"address": "914522, Владимирская область, город Волоколамск, проезд Ломоносова, 65", "id": 3},
             {"address": "658672, Тульская область, город Шаховская, спуск Домодедовская, 86", "id": 4},
             {"address": "565546, Ивановская область, город Зарайск, шоссе Гоголя, 31", "id": 5},
             {"address": "044316, Курская область, город Шатура, спуск Будапештсткая, 90", "id": 6},
             {"address": "119173, Калининградская область, город Кашира, пл. Гоголя, 43", "id": 7},
             {"address": "527168, Тверская область, город Озёры, пр. Ленина, 09", "id": 8}]

ORDERS = [
    {
        "id": 1,
        "items": [1, 2, 3]
    },
    {
        "id": 2,
        "items": [4, 5, 6]
    }
]

def hello(request):
    return render(request, "cards.html")

def GetCardInfo(id):
    return ADDRESSES[id - 1]

def GetAddresses(request):
    if request.method == "GET":
        return render(request, "cards.html", {"data": {
            "addresses": ADDRESSES,
        }})
    if request.method == "POST":
        query = request.POST.get('text')
        print(query)
        if not query:
            return render(request, "cards.html", {"data": {
                "addresses": ADDRESSES
            }})
        return render(request, "cards.html", {"data": {
            "addresses": list(filter(lambda x: query in x['address'].lower(), ADDRESSES))
        }})


def GetCard(request, id):
    return render(request, "card_desc.html", {'data': GetCardInfo(id)})

def GetOrders(request):
    return render(request, "orders.html", {"data": {
        "addresses": [ADDRESSES[i - 1] for i in ORDERS[0]['items']]
    }})