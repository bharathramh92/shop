from django.shortcuts import render
from django.core import serializers
from category_tree.models import Category
import json
from collections import defaultdict


# Create your views here.
def reset_view(request):

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
            return [data_map[d]["category_name"] for d in tree.keys()]

        def get_store_end_categories():

            end_categories = []

            def go(dc):
                for k, v in dc.items():
                    if not v:
                        end_categories.append((k, data_map[k]["category_name"]))
                    go(v)
            for store in tree.keys():
                go(tree[store])
            return end_categories

        data_str = "data = " + str(data_map) + "\n"
        store_names = "store_names = " + str(get_store_names()) + "\n"
        final_categories = "final_categories = " + str(get_store_end_categories()) + "\n"
        tree = "tree = " + str(tree) + "\n"
        out_file.write(data_str + store_names + final_categories + tree)
    return render(request, "category_tree/reset_successful.html", {})
