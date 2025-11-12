from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        unique_together = ['name', 'user']  # Category names unique per user
        indexes = [
            models.Index(fields=['user', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})

    @property
    def expense_count(self):
        """Return the number of expenses in this category"""
        return self.expenses.count()

    @property
    def total_expenses(self):
        """Return the total amount of expenses in this category"""
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0

class Expense(models.Model):
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount must be greater than 0"
    )
    description = models.CharField(
        max_length=200,
        help_text="Brief description of the expense"
    )
    date = models.DateField(
        default=timezone.now,
        help_text="Date when the expense occurred"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='expenses',
        help_text="Category for this expense"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category', 'date']),
        ]
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.amount} - {self.description} ({self.date})"

    def get_absolute_url(self):
        return reverse('expense-detail', kwargs={'pk': self.pk})

    @property
    def formatted_amount(self):
        """Return formatted amount with currency symbol"""
        return f"${self.amount}"

    def save(self, *args, **kwargs):
        """Custom save method to ensure data integrity"""
        # Ensure the category belongs to the same user
        if self.category.user != self.user:
            raise ValueError("Category must belong to the same user as the expense")
        
        # Ensure date is not in the future
        if self.date > timezone.now().date():
            raise ValueError("Expense date cannot be in the future")
            
        super().save(*args, **kwargs)