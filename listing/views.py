from django.shortcuts import render, HttpResponse, get_object_or_404
from store_db.models import BookStore, Item
from seller.ranking import get_ranked_inventory_list
from django.shortcuts import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from category_tree.categories import store_names


@csrf_exempt
def search_view(request):
    if request.method == 'POST':
        raise Http404
    if request.method == 'GET':
        if "store" not in request.GET:
            raise Http404
        store = request.GET.get("store")
        q = request.GET.get("q", "")
        print(store, q)

        # validate store and q
        try:
            store = int(store)
        except ValueError:
            raise Http404

        if store == -1:
            store_names_list = list(store_names.values())
        else:
            if store not in store_names:
                raise Http404
            store_names_list = [store_names[store]]

        item_list = list()          # items to display
        for st_name in store_names_list:
            if st_name == "Books":
                # basic filter for now
                item_list = Item.objects.filter(title__icontains=q)

        paginator = Paginator(item_list, 25) # Show 25 contacts per page

        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            results = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            results = paginator.page(paginator.num_pages)

        return render(request, 'listing/search_result.html', {'results': results})


def index_view(request):
    return render(request, "listing/index.html", {})


def department_view(request, department_id):
    return render(request, "listing/department.html", {})


def all_department_view(request):
    return HttpResponse("Show all departments list")


def book_item(request, pk):
    book_data = get_object_or_404(BookStore, pk=pk)
    ranked_inventories = get_ranked_inventory_list(book_data.item)
    return render(request, "listing/book_view.html", {'book_data': book_data, 'ranked_inventories': ranked_inventories})


def listing_item_view(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        return book_item(request, item.book_store_item.pk)
    except Item.DoesNotExist:
        pass
        raise Http404


def add_to_cart_view(request):
    try:
        seller = request.GET['seller']
        item_slug = request.GET['item_slug']
    except KeyError:
        raise Http404
    print(seller, item_slug)
    return HttpResponse("Add to cart. Temp!")
