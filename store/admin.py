from django.contrib import admin

from .models import Category, Product

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    # here slug which is url_name for category is created randomly from the name
    prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','author','slug','price','in_stock','created','updated']
    list_filter = ['in_stock','is_active']
    list_editable = ['price','in_stock']
    prepopulated_fields = {'slug':('title',)}

    