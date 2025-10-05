from django.contrib import admin
from .models import Category, Expense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'category', 'user', 'date')
    list_filter = ('category', 'date', 'user')
    search_fields = ('description',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'