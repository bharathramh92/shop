#!/usr/bin/env python
from django.core import serializers
# from category_tree.models import Category
import json
from collections import defaultdict

if __name__ == '__main__':
    # data = serializers.serialize('json', Category.objects.all())
    data = '[{"model": "category_tree.category", "pk": 1, "fields": {"category_name": "Books", "description": "", "parent_category": null}}, {"model": "category_tree.category", "pk": 2, "fields": {"category_name": "Arts & Photography", "description": "", "parent_category": 1}}, {"model": "category_tree.category", "pk": 3, "fields": {"category_name": "Architecture", "description": "", "parent_category": 2}}, {"model": "category_tree.category", "pk": 4, "fields": {"category_name": "CookBooks, Food & Wine", "description": "", "parent_category": 1}}, {"model": "category_tree.category", "pk": 5, "fields": {"category_name": "Asian Cooking", "description": "", "parent_category": 4}}, {"model": "category_tree.category", "pk": 6, "fields": {"category_name": "Baking", "description": "", "parent_category": 4}}, {"model": "category_tree.category", "pk": 7, "fields": {"category_name": "Computer & Technology", "description": "", "parent_category": 1}}, {"model": "category_tree.category", "pk": 8, "fields": {"category_name": "Database & BigData", "description": "", "parent_category": 7}}, {"model": "category_tree.category", "pk": 9, "fields": {"category_name": "Data Mining", "description": "", "parent_category": 8}}, {"model": "category_tree.category", "pk": 10, "fields": {"category_name": "Oracle", "description": "", "parent_category": 8}}, {"model": "category_tree.category", "pk": 11, "fields": {"category_name": "Programming", "description": "", "parent_category": 7}}, {"model": "category_tree.category", "pk": 12, "fields": {"category_name": "Algorithms", "description": "", "parent_category": 11}}, {"model": "category_tree.category", "pk": 13, "fields": {"category_name": "Data Structures", "description": "", "parent_category": 12}}, {"model": "category_tree.category", "pk": 14, "fields": {"category_name": "Genetic", "description": "", "parent_category": 12}}, {"model": "category_tree.category", "pk": 15, "fields": {"category_name": "Mobile Apps", "description": "", "parent_category": 11}}]'
    data = json.loads(data)
    data_map = {dt["pk"]: dt["fields"] for dt in data}

    list_data = defaultdict(list)

    for items in data:
        list_data[items['fields']['parent_category']].append((items['pk'], items['fields']['category_name'], items['fields']['parent_category']))


    def build_tree(dc, index):
        return {pk: build_tree(dc, pk) for pk, name, parent_id in dc[index]}

    tree = build_tree(list_data, None)

    with open("categories.py", "w", encoding="utf-8") as out_file:

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
        end_categories = "end_categories = " + str(get_store_end_categories()) + "\n"
        tree = "tree = " + str(tree) + "\n"
        out_file.write(data_str + store_names + end_categories + tree)