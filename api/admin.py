from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.contrib.auth.models import User  # Add this import
from .models import Category, Expense

class ExpenseInline(admin.TabularInline):
    """Inline editing for expenses in Category admin"""
    model = Expense
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('amount', 'description', 'date', 'created_at')
    can_delete = True
    show_change_link = True

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'expense_count', 'total_expenses', 'created_at')
    list_filter = ('created_at', 'user', 'updated_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'expense_count', 'total_expenses')
    list_per_page = 25
    inlines = [ExpenseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'description')
        }),
        ('Statistics', {
            'fields': ('expense_count', 'total_expenses'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def expense_count(self, obj):
        """Display the number of expenses in this category"""
        return obj.expenses.count()
    expense_count.short_description = 'Number of Expenses'

    def total_expenses(self, obj):
        """Display the total amount of expenses in this category"""
        total = obj.expenses.aggregate(total=Sum('amount'))['total']
        return f"${total:.2f}" if total else "$0.00"
    total_expenses.short_description = 'Total Expenses'

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('expenses')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'formatted_amount', 
        'description', 
        'category', 
        'user', 
        'date', 
        'days_ago'
    )
    list_filter = (
        'category', 
        'date', 
        'user', 
        'category__user',
        'created_at'
    )
    search_fields = (
        'description', 
        'category__name', 
        'user__username',
        'amount'
    )
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'days_ago',
        'formatted_amount_display'
    )
    date_hierarchy = 'date'
    list_per_page = 50
    list_select_related = ('category', 'user')
    
    fieldsets = (
        ('Expense Details', {
            'fields': (
                'amount', 
                'formatted_amount_display',
                'description', 
                'date',
                'category', 
                'user'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at', 
                'days_ago'
            ),
            'classes': ('collapse',)
        }),
    )

    def formatted_amount(self, obj):
        """Display amount with currency formatting in list view"""
        # FIX: Handle None values
        if obj.amount is None:
            return "$0.00"
        try:
            return f"${float(obj.amount):.2f}"
        except (TypeError, ValueError):
            return "$0.00"
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'

    def formatted_amount_display(self, obj):
        """Display amount with currency formatting in detail view"""
        # FIX: Handle None values - THIS WAS CAUSING THE ERROR
        if obj.amount is None:
            return "$0.00"
        try:
            return f"${float(obj.amount):.2f}"
        except (TypeError, ValueError):
            return "$0.00"
    formatted_amount_display.short_description = 'Formatted Amount'

    def days_ago(self, obj):
        """Display how many days ago the expense was created"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        if obj.created_at:
            return timesince(obj.created_at) + ' ago'
        return 'Unknown'
    days_ago.short_description = 'Created'

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('category', 'user')

    def get_list_display_links(self, request, list_display):
        """Make description clickable for editing"""
        return ['description']

    def get_readonly_fields(self, request, obj=None):
        """Make user field readonly when editing existing object"""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """Auto-set user if not set when creating"""
        if not change:  # If creating a new object
            if not obj.user_id:
                obj.user = request.user
        super().save_model(request, obj, form, change)

class UserExpenseFilter(admin.SimpleListFilter):
    """Custom filter for expenses by user"""
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        """Return list of users who have expenses"""
        users = User.objects.filter(expenses__isnull=False).distinct()
        return [(user.id, user.username) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id=self.value())
        return queryset

# Optional: Add actions for bulk operations
def update_category_description(modeladmin, request, queryset):
    """Admin action to update category descriptions"""
    count = queryset.update(description="Updated via admin action")
    modeladmin.message_user(request, f"Updated {count} categories.")
update_category_description.short_description = "Update selected categories descriptions"

def mark_expenses_as_reviewed(modeladmin, request, queryset):
    """Admin action to mark expenses as reviewed (if you add a reviewed field later)"""
    # This is a placeholder for when you add a 'reviewed' boolean field
    # count = queryset.update(reviewed=True)
    # modeladmin.message_user(request, f"Marked {count} expenses as reviewed.")
    modeladmin.message_user(request, "This action would mark expenses as reviewed.")
mark_expenses_as_reviewed.short_description = "Mark expenses as reviewed"

# Add actions to admin classes
CategoryAdmin.actions = [update_category_description]
ExpenseAdmin.actions = [mark_expenses_as_reviewed]