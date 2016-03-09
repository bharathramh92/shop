from django.db import models


class Category(models.Model):

    category_name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    parent_category = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return self.category_name
