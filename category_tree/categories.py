data = {1: {'category_name': 'Books', 'description': '', 'parent_category': None}, 2: {'category_name': 'Arts & Photography', 'description': '', 'parent_category': 1}, 3: {'category_name': 'Architecture', 'description': '', 'parent_category': 2}, 4: {'category_name': 'CookBooks, Food & Wine', 'description': '', 'parent_category': 1}, 5: {'category_name': 'Asian Cooking', 'description': '', 'parent_category': 4}, 6: {'category_name': 'Baking', 'description': '', 'parent_category': 4}, 7: {'category_name': 'Computer & Technology', 'description': '', 'parent_category': 1}, 8: {'category_name': 'Database & BigData', 'description': '', 'parent_category': 7}, 9: {'category_name': 'Data Mining', 'description': '', 'parent_category': 8}, 10: {'category_name': 'Oracle', 'description': '', 'parent_category': 8}, 11: {'category_name': 'Programming', 'description': '', 'parent_category': 7}, 12: {'category_name': 'Algorithms', 'description': '', 'parent_category': 11}, 13: {'category_name': 'Data Structures', 'description': '', 'parent_category': 12}, 14: {'category_name': 'Genetic', 'description': '', 'parent_category': 12}, 15: {'category_name': 'Mobile Apps', 'description': '', 'parent_category': 11}}
store_names = {1: 'Books'}
store_names_reverse_map = {'Books': 1}
final_categories = {1: [(3, 'Architecture'), (5, 'Asian Cooking'), (6, 'Baking'), (9, 'Data Mining'), (10, 'Oracle'), (13, 'Data Structures'), (14, 'Genetic'), (15, 'Mobile Apps')],
                    2: [(3, 'Architecture')],
                    4: [(5, 'Asian Cooking'), (6, 'Baking')],
                    8: [(9, 'Data Mining'), (10, 'Oracle')],
                    11: [(15, 'Mobile Apps')],
                    12: [(13, 'Data Structures'), (14, 'Genetic')]}
tree = {1: {2: {3: {}}, 4: {5: {}, 6: {}}, 7: {8: {9: {}, 10: {}}, 11: {12: {13: {}, 14: {}}, 15: {}}}}}
store_name_from_child = {3: 2, 5: 4, 6: 4, 9: 8, 10: 8, 13: 12, 14: 12, 15: 11}
tree_name = {'Books': {'CookBooks, Food & Wine': {'Baking': {}, 'Asian Cooking': {}}, 'Arts & Photography': {'Architecture': {}}, 'Computer & Technology': {'Database & BigData': {'Oracle': {}, 'Data Mining': {}}, 'Programming': {'Mobile Apps': {}, 'Algorithms': {'Data Structures': {}, 'Genetic': {}}}}}}
