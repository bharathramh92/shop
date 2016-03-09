#!/usr/bin/env python
import json

if __name__ == '__main__':
    with open("categories.json", "r", encoding="utf-8") as in_file, \
            open("categories.py", "w", encoding="utf-8") as out_file:
        def get_category_store_names():
            return [d for d in data.keys()]


        def get_store_end_categories():
            out = []

            def go(dc):
                for k, v in dc.items():
                    if not v:
                        out.append(k)
                    go(v)
            for store in get_category_store_names():
                go(data[store])
            return out

        data = json.loads(in_file.read())
        data_str = "data = " + str(data) + "\n"
        store_names = "store_names = " + str(get_category_store_names()) + "\n"
        final_categories = "final_categories = " + str(get_store_end_categories()) + "\n"

        out_file.write(data_str + store_names + final_categories)