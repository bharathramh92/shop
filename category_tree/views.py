import json
from collections import defaultdict

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponseRedirect

from category_tree.models import Category


def reset_view(request):
    if not (request.user.is_authenticated() and request.user.is_superuser):
        # only the admin should be able to access this page
        return HttpResponseRedirect(reverse('listing:index'))

    data = serializers.serialize('json', Category.objects.all())
    data = json.loads(data)
    data_map = {dt["pk"]: dt["fields"] for dt in data}

    list_data = defaultdict(list)

    for items in data:
        list_data[items['fields']['parent_category']]\
            .append((items['pk'], items['fields']['category_name'], items['fields']['parent_category']))

    def build_tree(dc, index):
        return {pk: build_tree(dc, pk) for pk, name, parent_id in dc[index]}

    tree = build_tree(list_data, None)

    with open("category_tree/categories.py", "w", encoding="utf-8") as out_file:

        def get_store_names():
            return {d: data_map[d]["category_name"] for d in tree.keys()}

        end_categories_map = defaultdict(list)

        def get_store_end_categories():

            def go(dc, store_name):
                for k, v in dc.items():
                    if not v:
                        end_categories_map[store_name].append((k, data_map[k]["category_name"]))
                    go(v, store_name)
            for store in tree.keys():
                go(tree[store], store)
            return dict(end_categories_map)

        store_buffer = get_store_names()
        data_str = "data = " + str(data_map) + "\n"
        store_names = "store_names = " + str(store_buffer) + "\n"
        store_names_reverse_map = "store_names_reverse_map = " + str({v: k for k, v in store_buffer.items()}) + "\n"
        final_categories_map = "final_categories = " + str(get_store_end_categories()) + "\n"
        tree = "tree = " + str(tree) + "\n"
        out_file.write(data_str + store_names + store_names_reverse_map + final_categories_map + tree)
    return render(request, "category_tree/reset_successful.html", {})
