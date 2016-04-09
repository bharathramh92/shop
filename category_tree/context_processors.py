from category_tree.categories import store_names, data


def store_dict_processor(request):
    store_names['-1'] = "All"
    return {'store': store_names, 'categories_data': data}
