from django.shortcuts import render, HttpResponse, get_object_or_404
from store_db.models import BookStore
from seller.ranking import get_ranked_inventory_list


def index_view(request):
    return render(request, "listing/index.html", {})


def department_view(request, department_id):
    return render(request, "listing/department.html", {})


def all_department_view(request):
    return HttpResponse("Show all departments list")


def book_item_view(request, pk):
    book_data = get_object_or_404(BookStore, pk=pk)
    ranked_inventories = get_ranked_inventory_list(book_data.item)
    return render(request, "listing/book_view.html", {'book_data': book_data, 'ranked_inventories': ranked_inventories})
