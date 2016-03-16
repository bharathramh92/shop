import random

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from dal import autocomplete


from seller.forms import StoreSelectForm, NewBookForm, NewBookISBNCheckForm, ItemForm, \
    InventoryForm, NewAuthorForm, NewPublisherForm
from .forms import NewBookAuthorForm, NewBookPublisherForm
from store_db.models import BookStore, Item, Author, Publisher, Inventory
from category_tree.categories import *


def rand_alphanumeric(length=100):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(length))


def get_from_request_GET(request):
    return '?' + ''.join([str(k + '=' + v + '&') for k, v in request.GET.items()])[:-1]

###############################################################
# autocomplete-light


class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Return empty result if the user is not authenticated
        if not self.request.user.is_authenticated():
            return Author.objects.none()

        qs = Author.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class PublisherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Return empty result if the user is not authenticated
        if not self.request.user.is_authenticated():
            return Publisher.objects.none()

        qs = Publisher.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

###############################################################


@login_required()
def dashboard_view(request):
    inventory_list = Inventory.objects.filter(seller=request.user)
    paginator = Paginator(inventory_list, 25)  # Show 25 inventories per page

    page = request.GET.get('page')
    try:
        inventories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        inventories = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        inventories = paginator.page(paginator.num_pages)

    return render(request, 'seller/dashboard.html', {"inventories": inventories})


@login_required()
def new_view(request):
    # To redirect the user to their respective store.
    if request.method == 'POST':
        form = StoreSelectForm(request.POST)
        if form.is_valid():
            if store_names[int(request.POST.get('store_names'))] == 'Books':
                return HttpResponseRedirect(reverse('seller:new_book_check'))

            return HttpResponseRedirect(reverse('seller:new'))
        else:
            raise Http404("Store does not exist")
    else:
        form = StoreSelectForm()

    return render(request, "seller/new.html", {'storeForm': form})


@login_required()
def add_new_book_pk_check(request):
    if request.method == 'POST':
        form = NewBookISBNCheckForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['isbn']
            try:
                book = BookStore.objects.get(pk=isbn)
                if Inventory.objects.filter(item=book.item) != 0:
                    # If the user tries to add his previously added book again, we will redirect him to edit inventory.
                    return HttpResponse(reverse('seller:edit_inventory'))

                data_dict = {'store': store_names_reverse_map['Books'], 'id': book.pk}
                get = '?'
                for k, v in data_dict.items():
                    get += k + '=' + v
                return HttpResponse(reverse('seller:new_inventory') + get)
            except ObjectDoesNotExist:
                # if not found, create a new book
                return HttpResponseRedirect(reverse('seller:new_book', kwargs={'isbn': isbn}))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewBookISBNCheckForm()

    return render(request, "seller/new_book_isbn_check.html", {'isbnCheckForm': form})



@login_required()
def add_new_book(request, isbn):
    store_id = store_names_reverse_map["Books"]
    forms = {}
    try:
        # double checking isbn format, since a direct request to this url could break our desired outcome.
        if len(str(int(isbn))) == 13:
            BookStore.objects.get(isbn_13=isbn)
            return HttpResponseRedirect(reverse("seller:new_book_check"))
        else:
            raise PermissionDenied
    except ObjectDoesNotExist:
        pass
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        bookForm = NewBookForm(request.POST, isbn=isbn)
        itemForm = ItemForm(request.POST, store_id=store_id)
        authorForm = NewBookAuthorForm(request.POST)
        publisherForm = NewBookPublisherForm(request.POST)

        forms['bookForm'] = bookForm
        forms['itemForm'] = itemForm
        forms['authorForm'] = authorForm
        forms['publisherForm'] = publisherForm
        forms['isbn'] = isbn

        # check whether it's valid:
        if bookForm.is_valid() and itemForm.is_valid() and authorForm.is_valid() and publisherForm.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            title = itemForm.cleaned_data['title']
            description = itemForm.cleaned_data['description']
            shipping_product_dimension_height = itemForm.cleaned_data['shipping_product_dimension_height']
            shipping_product_dimension_width = itemForm.cleaned_data['shipping_product_dimension_width']
            shipping_product_dimension_length = itemForm.cleaned_data['shipping_product_dimension_length']
            shipping_product_dimension_units = itemForm.cleaned_data['shipping_product_dimension_units']
            shipping_product_weight = itemForm.cleaned_data['shipping_product_weight']
            shipping_product_weight_units = itemForm.cleaned_data['shipping_product_weight_units']
            category = itemForm.cleaned_data['category']
            item = Item.objects.create(title= title, description= description, shipping_product_dimension_height= shipping_product_dimension_height,
                                       shipping_product_dimension_width= shipping_product_dimension_width, shipping_product_dimension_length= shipping_product_dimension_length,
                                       shipping_product_dimension_units= shipping_product_dimension_units, shipping_product_weight= shipping_product_weight,
                                       shipping_product_weight_units= shipping_product_weight_units)
            item.category.add(*category)

            isbn_10 = bookForm.cleaned_data['isbn_10']
            isbn_13 = bookForm.cleaned_data['isbn_13']
            language = bookForm.cleaned_data['language']
            publisher = publisherForm.cleaned_data['test']

            book = BookStore.objects.create(isbn_10=isbn_10, isbn_13=isbn_13, language=language,
                                            item=item, publisher=publisher)
            authors = authorForm.cleaned_data['test']
            book.authors.add(*authors)

            new_inventory_redirect = reverse('seller:new_inventory') + '?store_id=' + str(store_id) + '&isbn_13=' + str(isbn_13)
            return HttpResponseRedirect(new_inventory_redirect)
        print("b", bookForm.errors)
        print("i", itemForm.errors)
        print("A", authorForm.errors)
        print("p", publisherForm.errors)
    # if a GET (or any other method) we'll create a blank form
    else:

        forms['bookForm'] = NewBookForm(isbn=isbn)
        forms['itemForm'] = ItemForm(store_id=store_id)
        forms['authorForm'] = NewBookAuthorForm()
        forms['publisherForm'] = NewBookPublisherForm()
        forms['isbn'] = isbn
    return render(request, "seller/new_book.html", forms)


class StoreNotFoundException(Exception):
    pass


@login_required()
def new_inventory_view(request):
    try:    # Proceed only if object exists for that store.
        store_id = int(request.GET['store_id'])
        # retrieve item object as well
        if store_id == store_names_reverse_map["Books"]:
            isbn_13 = request.GET['isbn_13']
            book = BookStore.objects.get(isbn_13=isbn_13)
            item = book.item
            if len(Inventory.objects.filter(item=item, seller=request.user)) != 0:
                return render(request, 'seller/new_inventory_present_already.html', {})
        else:
            print("storenotfound")
            raise StoreNotFoundException

    except (ObjectDoesNotExist, StoreNotFoundException, KeyError) as e:
        print(e)
        raise PermissionDenied
    except KeyError:
        raise Http404

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        inventoryForm = InventoryForm(request.POST, user=request.user)
        # check whether it's valid:
        if inventoryForm.is_valid():
            price = inventoryForm.cleaned_data['price']
            total_available_stock = inventoryForm.cleaned_data['total_available_stock']
            item_location = inventoryForm.cleaned_data['item_location']
            free_domestic_shipping = inventoryForm.cleaned_data['free_domestic_shipping']
            local_pick_up_accepted = inventoryForm.cleaned_data['local_pick_up_accepted']
            dispatch_max_time = inventoryForm.cleaned_data['dispatch_max_time']
            return_accepted = inventoryForm.cleaned_data['return_accepted']
            listing_end_datetime = inventoryForm.cleaned_data['listing_end_datetime']
            condition = inventoryForm.cleaned_data['condition']

            # domestic_shipping_company = inventoryForm.cleaned_data['domestic_shipping_company']
            # domestic_shipping_cost = inventoryForm.cleaned_data['domestic_shipping_cost']
            # international_shipping_company = inventoryForm.cleaned_data['international_shipping_company']
            # international_shipping_cost = inventoryForm.cleaned_data['international_shipping_cost']
            # free_international_shipping = inventoryForm.cleaned_data['free_international_shipping']
            # available_countries = inventoryForm.cleaned_data['available_countries']

            Inventory.objects.create(item=item, seller=request.user, price=price, total_available_stock= total_available_stock,
                                     item_location= item_location, free_domestic_shipping= free_domestic_shipping,
                                     local_pick_up_accepted= local_pick_up_accepted,
                                     dispatch_max_time= dispatch_max_time, return_accepted= return_accepted,
                                     listing_end_datetime= listing_end_datetime, condition= condition,)
            return render(request, 'seller/new_inventory_added.html', {})

    # if a GET (or any other method) we'll create a blank form
    else:
        inventoryForm = InventoryForm(user= request.user)
    return render(request, 'seller/new_inventory.html', {'inventoryForm': inventoryForm, 'get_params': get_from_request_GET(request)})


class InventoryNotFoundException(Exception):
    pass


@login_required()
def edit_inventory_view(request, pk):
    try:    # Proceed only if object exists for that store.
        inventory = Inventory.objects.get(pk=pk, seller=request.user)
    except ObjectDoesNotExist:
        raise Http404("Inventory does not exist")

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory, user=request.user, item_location=inventory.item_location)
        if form.is_valid():
            inventory.price = form.cleaned_data['price']
            inventory.total_available_stock = form.cleaned_data['total_available_stock']
            inventory.address = form.cleaned_data['item_location']
            inventory.free_domestic_shipping = form.cleaned_data['free_domestic_shipping']
            inventory.local_pick_up_accepted = form.cleaned_data['local_pick_up_accepted']
            inventory.dispatch_max_time = form.cleaned_data['dispatch_max_time']
            inventory.return_accepted = form.cleaned_data['return_accepted']
            inventory.listing_end_datetime = form.cleaned_data['listing_end_datetime']
            inventory.condition = form.cleaned_data['condition']
            inventory.save()
            return render(request, 'seller/edit_inventory.html',
                          {'inventoryForm': form, 'pk': pk, 'message': "Inventory Updated"})
    else:
        form = InventoryForm(instance=inventory, user=request.user, item_location=inventory.item_location)

    return render(request, 'seller/edit_inventory.html', {'inventoryForm': form, 'pk': pk})


@login_required()
def new_author(request):
    pass
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewAuthorForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            name = form.cleaned_data['name']
            Author.objects.create(name = name, created_by = request.user)
            return render(request, 'seller/new_author_added.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewAuthorForm()

    return render(request, 'seller/new_author.html', {'form': form})


@login_required()
def new_publisher(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewPublisherForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            name = form.cleaned_data['name']
            Publisher.objects.create(name=name, created_by=request.user)
            return render(request, 'seller/new_publisher_added.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewPublisherForm()

    return render(request, 'seller/new_publisher.html', {'form': form})
