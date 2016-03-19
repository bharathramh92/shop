from django.db.models import Q, Sum, Count

from store_db.models import SellerFeedback, Inventory, SellerRating


def rank_seller_from_inventory(inventory):
    # call this method if inventory is added/updated or new feedback is received
    # based on seller_points,  return_accepted, local_pickup, free_domestic_shipping
    rank_seller(inventory.seller)
    total_points = inventory.seller.seller_rank.points
    if inventory.return_accepted:
        total_points += 10
    if inventory.local_pick_up_accepted:
        total_points += 10
    if inventory.free_domestic_shipping:
        total_points += 100
    inventory.rating = total_points
    print(total_points)
    inventory.save()


def rank_seller(seller):
    # call this method if feedback is created/edited or if new sales are made.
    # maximum review points is 5
    total_sales_made = Inventory.objects.filter(seller=seller).aggregate(tsm=Sum('total_sold'))
    total_sales_made= total_sales_made['tsm']
    sfd = SellerFeedback.objects.filter(seller=seller).aggregate(total_review_points=Sum('review_points'),
                                                                number_of_reviews=Count('review_points'))
    if sfd['total_review_points'] is None:
        sfd['total_review_points'] = 0
    if total_sales_made == 0:
        seller_rating_points = 100
    else:
        seller_rating_points = (total_sales_made-sfd['number_of_reviews'])*5 + sfd['total_review_points']/sfd['total_sales_made']
    SellerRating.objects.update_or_create(seller=seller, defaults={'points': seller_rating_points})


def get_ranked_inventory_list(item):
    inventories = item.item_inventory.all()
    return inventories.order_by('-rating')
