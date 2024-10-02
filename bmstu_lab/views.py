from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from bmstu_lab.models import * 


def index(request):
    search_address = request.GET.get("search_address", "")
    addresses = Address.objects
    if search_address: 
        addresses = addresses.filter(address__icontains=search_address)
    else:
        addresses = addresses.all()

    # draft_fixations = get_draft_fixations()
    context = {
        "search_address": search_address,
        "addresses": addresses
    }

    # if draft_fixations:
    #     context["climbers_count"] = len(draft_fixations.get_climbers())
    #     context["draft_expedition"] = draft_fixations

    return render(request, "cards.html", context)

def address_details(request, id):
    context = {
        "address": Address.objects.get(id=id)
    }
    return render(request, "card_desc.html", context)

def fixation_details(request, id):
    if not Fixation.objects.filter(pk=id).exists():
        return redirect("/")
    if Fixation.objects.get(id=id).status == 5:
        return redirect("/")
    
    context = {
        "fixation": Fixation.objects.get(id=id),
    }
    return render(request, "orders.html", context)

def del_fixation(request, id):
    if not Fixation.objects.filter(pk=id).exists():
        return redirect("/")
    with connection.cursor() as cursor:
        cursor.execute("UPDATE fixations SET status = 5 WHERE id = %s", [id])
    return redirect("/")

def add_address(request, id):
    address = Address.objects.get(pk=id)

    draft_fixations = get_draft_fixations()

    if draft_fixations is None:
        draft_fixations = Fixation.objects.create()
        draft_fixations.owner = get_current_user()
        draft_fixations.date_created = timezone.now()
        draft_fixations.save()

    if AddressFixation.objects.filter(fixation=draft_fixations, address=address).exists():
        return redirect("/")

    item = AddressFixation(
        fixation=draft_fixations,
        address=address
    )
    item.save()

    return redirect("/")

def get_draft_fixations():
    return Fixation.objects.filter(status=1).first()

def get_current_user():
    return User.objects.filter(is_superuser=False).first()