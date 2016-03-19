from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Address
from category_tree.models import Category
###################################################################################


# items
class Item(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    shipping_product_dimension_height = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    shipping_product_dimension_width = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    shipping_product_dimension_length = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    INCHES, FEET, MILLIMETERS, CENTIMETERS = "IN", "FT", "MM", "CM"
    DIMENSION_CHOICES = (
        (INCHES, 'Inches'),
        (FEET, 'Feet'),
        (MILLIMETERS, 'Millimeters'),
        (CENTIMETERS, 'Centimeters'),
    )
    shipping_product_dimension_units = models.CharField(max_length=2, choices=DIMENSION_CHOICES,
                                                        default=INCHES, null=False, blank=False)

    shipping_product_weight = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    OUNCES, POUNDS, MILLIGRAMS, GRAMS, KILOGRAMS = "OZ", "LB", "MG", "G", "KG"
    WEIGHT_CHOICES = (
        (OUNCES, 'Ounces'),
        (POUNDS, 'Pounds'),
        (MILLIGRAMS, 'Milligrams'),
        (GRAMS, 'Grams'),
        (KILOGRAMS, 'Kilograms'),
    )
    shipping_product_weight_units = models.CharField(max_length=2, choices=WEIGHT_CHOICES, default=OUNCES,
                                                     null=False, blank=False)
    # one item can be in multiple categories, but in a same store
    category = models.ManyToManyField(Category, related_name='main_sub_cat_item')
    posting_datetime = models.DateTimeField(default=timezone.now, null=False, blank=False)
    last_updated_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class ItemMedia(models.Model):
    item = models.ForeignKey(Item, related_name='item_media')
    url = models.CharField(max_length=250, null=False, blank=False)
    title = models.CharField(max_length=100, null=True, blank=True)
    PHOTO, VIDEO = "P", "V"
    MEDIA_CHOICES = (
        (PHOTO, "Photo"),
        (VIDEO, "Video")
    )
    photo_or_video = models.CharField(max_length=1, choices=MEDIA_CHOICES, default=PHOTO, null=False, blank=False)
    added_datetime = models.DateTimeField(default=timezone.now, null=False, blank=False)


class Inventory(models.Model):
    """
    Item Seller interface
    """
    item = models.ForeignKey(Item, related_name='item_inventory')
    seller = models.ForeignKey(User, related_name='seller_inventory', on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=19, decimal_places=4)
    # http://www.xe.com/iso4217.php use this to populate
    currency = models.CharField(max_length=3, default='USD', null=False, blank=False)
    total_available_stock = models.PositiveIntegerField(null=False, blank=False)
    total_sold = models.PositiveIntegerField(default=0, null=False, blank=False)

    item_location = models.ForeignKey(Address, related_name='item_location_address')
    free_domestic_shipping = models.BooleanField(null=False, blank=False)

    # domestic_shipping_company = models.CharField(max_length=100, null=True, blank=True)
    # domestic_shipping_cost = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)

    # DOMESTIC, WORLDWIDE = "Domestic", "Worldwide"
    # AVAILABLE_COUNTRY_CHOICES = (
    #     (DOMESTIC, "Domestic"),
    #     (WORLDWIDE, "Worldwide")
    # )
    # # origin country or worldwide
    # available_countries = models.CharField(max_length=12, choices=AVAILABLE_COUNTRY_CHOICES,
    #                                        default=WORLDWIDE, null=False, blank=False)
    # international_shipping_company = models.CharField(max_length=100, null=True, blank=True)
    # international_shipping_cost = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    # free_international_shipping = models.BooleanField(null=False, blank=False)

    local_pick_up_accepted = models.BooleanField(null=False, blank=False)

    dispatch_max_time = models.PositiveIntegerField(null=False, blank=False)    # in hours
    return_accepted = models.BooleanField(null=False, blank=False)

    listing_end_datetime = models.DateTimeField(default=timezone.now, null=False, blank=False)

    NEW, USED = 'n', 'u'
    CONDITION_CHOICES = (
        (NEW, "New"),
        (USED, "Used"),
    )
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, default=NEW, null=False, blank=False)
    visibility = models.BooleanField(default=True)

    rating = models.PositiveIntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return "%s... by %s %s" % (self.item.title[:20], self.seller.first_name, self.seller.last_name)

    def has_expired(self):
        return self.listing_end_datetime < timezone.now()


# remaining details are pending for payment
# class Payment(models.Model):
#     tax = models.DecimalField(max_digits=19, decimal_places= 4)
#     total_amount_payed = models.DecimalField(max_digits=19, decimal_places= 4)
#     payment_method = models.CharField(max_length=50)

# class Invoice(models.Model):
#     payment = models.OneToOneField(Payment)
#     order_datetime = models.DateTimeField(default= timezone.now)

class Order(models.Model):
    inventory = models.ForeignKey(Inventory, related_name='inventory_order')
    # tracking_number = models.CharField(max_length=30, null=False, blank=False)
    # shipping_company = models.CharField(max_length=50, null=False, blank=False)
    # shipping_datetime = models.DateTimeField(null=True, blank=True)
    # delivery_datetime = models.DateTimeField(null=True, blank=True)

    quantity = models.PositiveIntegerField(null=False, blank=False)
    item_returned = models.NullBooleanField()
    completed = models.BooleanField(default=False, null=False, blank=False)

    # invoice = models.ForeignKey(Invoice)


class Dispute(models.Model):
    order = models.ForeignKey(Order, related_name="order_no_disputes")
    message = models.CharField(max_length=1000, null=False, blank=False)
    ACCEPTED, DECLINED, PENDING = "ACC", "DEC", "PEN"
    DISPUTE_STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DECLINED, "Declined")
    )
    status = models.CharField(max_length=1, choices=DISPUTE_STATUS_CHOICES, default=PENDING, null=False, blank=False)


class Cart(models.Model):
    item = models.ForeignKey(Item, related_name="item_in_cart")
    quantity = models.PositiveIntegerField(null=False, blank=False)
    user = models.ForeignKey(User, related_name="cart_user", on_delete=models.CASCADE)
    added_or_updated_datetime = models.DateTimeField(default=timezone.now)

#############################################################################


# Feedback
class ContactUs(models.Model):
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=1000, null=False, blank=False)


class ItemFeedback(models.Model):
    user_reviewed = models.ForeignKey(User, related_name="user_item_review")
    item = models.ForeignKey(Item, related_name='item_in_feedback')
    rating = models.PositiveSmallIntegerField(null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    visibility = models.BooleanField(default=False, null=False, blank=False)
    posting_datetime = models.DateTimeField(default=timezone.now)
    last_updated_datetime = models.DateTimeField(null=True, blank=True)


class SellerFeedback(models.Model):
    reviewer = models.ForeignKey(User, related_name='reviewed_by')
    seller = models.ForeignKey(User, related_name='seller', on_delete=models.CASCADE)
    review_description = models.CharField(max_length=1000, null=False, blank=False)
    review_points = models.PositiveSmallIntegerField(null=False, blank=False)
    posting_datetime = models.DateTimeField(default=timezone.now)
    last_updated_datetime = models.DateTimeField(null=True, blank=True)

##################################################################################


# Book Store
class Publisher(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True )

    test = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='related_publisher_test_models'
    )

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True)

    test = models.ManyToManyField(
        'self',
        blank=True,
        related_name='related_test_models'
    )

    def __str__(self):
        return self.name


class BookStore(models.Model):
    item = models.OneToOneField(Item, related_name='book_store_item')
    isbn_10 = models.CharField(max_length=10, unique=True)
    isbn_13 = models.CharField(max_length=13, unique=True)
    ENGLISH, FRENCH = "eng", "fre"
    LANGUAGE_CHOICE = (
        (ENGLISH, "English"),
        (FRENCH, "French")
    )
    language = models.CharField(max_length=3, choices=LANGUAGE_CHOICE, default=ENGLISH, null=False, blank=False)

    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)

    def get_book_name(self):
        return self.item.title

##########################################################################


class SellerRating(models.Model):
    seller = models.OneToOneField(User, related_name='seller_rank', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(null=False, blank=False)


