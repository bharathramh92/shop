from django import forms
from store_db.models import BookStore, Item, Author, Publisher, Inventory
from category_tree.categories import store_names, final_categories
from accounts.models import Address
from django.core.exceptions import ObjectDoesNotExist
from dal import autocomplete
from datetimewidget.widgets import DateTimeWidget


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        store_id = kwargs.pop('store_id', None)
        super(ItemForm, self).__init__(*args, **kwargs)
        category_choices = final_categories[store_id]
        self.fields['category'] = forms.MultipleChoiceField(label="Select Categories", choices=category_choices)

    class Meta:
        model = Item
        exclude = ['posting_datetime', 'last_updated_datetime', 'slug']


class StoreSelectForm(forms.Form):
    store_name_choices = store_names.items()
    store_names = forms.ChoiceField(label="Select a store", choices=store_name_choices)


class NewBookForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.isbn = kwargs.pop('isbn', None)
        super(NewBookForm, self).__init__(*args, **kwargs)

    class Meta(ItemForm.Meta):
        model = BookStore
        exclude = ['item', 'authors', 'publisher']

    def clean_isbn_13(self):
        isbn_13 = self.cleaned_data['isbn_13']
        try:
            int(isbn_13)
            if len(isbn_13) != 13:
                raise NotLen13ISBNException
            elif self.isbn is None or self.isbn != isbn_13:
                raise UnMatchedISBNException
        except ValueError:
            self.add_error('isbn_13', "ISBN 13 should be a number")
        except UnMatchedISBNException:
            self.add_error('isbn_13', "ISBN 13 which you previously validated and current isbn are not same. "
                                      "Please return to the previous page if you want change isbn.")
        except NotLen13ISBNException:
            self.add_error('isbn_13', "ISBN 13 should be of length 13")
        return isbn_13

    def clean_isbn_10(self):
        isbn = self.cleaned_data['isbn_10']
        try:
            int(isbn)
            if len(isbn) != 10:
                raise NotLen10ISBNException
        except ValueError:
            self.add_error('isbn_10', "ISBN 10 should be a number")
        except NotLen10ISBNException:
            self.add_error('isbn_10', "ISBN 10 should be of length 10")
        return isbn


class UnMatchedISBNException(Exception):
    pass


class NotLen10ISBNException(Exception):
    pass


class NotLen13ISBNException(Exception):
    pass


class NewBookISBNCheckForm(forms.Form):

    isbn = forms.CharField(max_length=13, min_length=13, label="ISBN", widget=forms.NumberInput())

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        try:
            int(isbn)
            if len(isbn) != 13:
                raise NotLen13ISBNException
        except ValueError:
            self.add_error('isbn', "ISBN should be a number")
        except NotLen13ISBNException:
            self.add_error('isbn', "ISBN should be of length 13")
        return isbn


class NewBookAuthorForm(forms.ModelForm):
    prefix = 'author'

    class Meta:
        model = Author
        fields = ['test', ]
        widgets = {
            'test': autocomplete.ModelSelect2Multiple(url='seller:author-autocomplete')
        }
        labels = {
            'test': "Authors",
        }


class NewBookPublisherForm(forms.ModelForm):
    prefix = "publisher"

    def __init__(self, *args, **kwargs):
        super(NewBookPublisherForm, self).__init__(*args, **kwargs)
        self.fields['test'].required = True

    class Meta:
        model = Publisher
        fields = ['test', ]
        widgets = {
            'test': autocomplete.ModelSelect2(url='seller:publisher-autocomplete')
        }
        labels = {
            'test': "Publisher",
        }

    def clean_test(self):
        data = self.cleaned_data['test']
        return data


class InventoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        address = kwargs.pop('item_location', None)
        super(InventoryForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['item_location'] = forms.ModelChoiceField(label="Item Location", initial=address,
                                                                  queryset=Address.objects.filter(user=user))

    class Meta:
        model = Inventory
        exclude = ['item', 'seller', 'total_sold', 'currency', 'visibility', 'rating', ]
        labels = {'condition': 'Item Condition', }
        widgets = {
            'listing_end_datetime': DateTimeWidget(attrs={'id': "listing_end_datetime"},
                                                   usel10n=True, bootstrap_version=3),
        }
        help_texts = {
            'dispatch_max_time': 'In hours',
            'free_domestic_shipping': 'If free shipping is not available,'
                                      ' standard shipping rates would be applied on the order.',
            'local_pick_up_accepted': 'Pick charge will always be free for the customer.',
        }


class NewAuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', ]

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            Author.objects.get(name__iexact=name)
            self.add_error('name', "Author already present. No need to add the same name."
                                   "Use " + name + " in required field directly.")
        except ObjectDoesNotExist:
            return name


class NewPublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', ]

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            Publisher.objects.get(name__iexact=name)
            self.add_error('name', "Publisher already present. No need to add the same name."
                                   "Use " + name + " in required field directly.")
        except ObjectDoesNotExist:
            return name
