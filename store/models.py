from django.db import models
from django.contrib.auth.models import User
"""
These are used to create table inside the databases

"""

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    slug = models.SlugField(max_length=255,unique=True)   # url name for the category

    # metadata for information for django on our table
    class Meta:
        # just telling django plural name for class
        verbose_name_plural = 'categories '

    # default name of the object
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category,related_name='product',on_delete=models.CASCADE)
    # Here User is an built in django model used for authentication
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='product_created')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255,default='admin')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/')
    slug = models.SlugField(max_length=25)
    price = models.DecimalField(max_digits=4,decimal_places=2)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',) # sort by descending order of the creation date

    def __str__(self):
        return self.title
    