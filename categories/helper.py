from categories.categories import data


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

