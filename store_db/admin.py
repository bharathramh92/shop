from django.contrib import admin
from store_db.models import *


# Register your models here.
class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'website', 'created_by', ]}),
    ]
    list_display = ('name', 'created_by')

admin.site.register(Author, AuthorAdmin)


class PublisherAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'description', 'website', 'created_by', 'contact_email']}),
    ]
    list_display = ('name', 'created_by')

admin.site.register(Publisher, PublisherAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', )

admin.site.register(Item, ItemAdmin)


class BookStoreAdmin(admin.ModelAdmin):
    list_display = ('get_book_name', )

admin.site.register(BookStore, BookStoreAdmin)
admin.site.register(Inventory)