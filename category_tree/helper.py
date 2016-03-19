from category_tree.categories import data


def get_store_name_from_child(store_id):
    while data[store_id]['parent_category'] is not None:
        store_id = data[store_id]['parent_category']
    return store_id
