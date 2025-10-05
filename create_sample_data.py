import os
import django
import sys

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

# Now import and setup Django
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from datetime import date, timedelta
from api.models import Category, Expense

def create_sample_data():
    print("📊 Creating sample data for Personal Expense Tracker...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='demo',
        email='demo@example.com'
    )
    if created:
        user.set_password('demopass123')
        user.save()
        print("✅ Created demo user: demo/demopass123")
    else:
        print("ℹ️ Demo user already exists")
    
    # Create categories
    categories_data = [
        {'name': 'Food', 'description': 'Groceries and dining out'},
        {'name': 'Transport', 'description': 'Travel expenses'},
        {'name': 'Entertainment', 'description': 'Movies, games, etc.'},
        {'name': 'Utilities', 'description': 'Bills and utilities'},
        {'name': 'Healthcare', 'description': 'Medical expenses'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            user=user,
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories.append(category)
        if created:
            print(f"✅ Created category: {cat_data['name']}")
        else:
            print(f"ℹ️ Category already exists: {cat_data['name']}")
    
    # Create sample expenses
    expenses_data = [
        {'amount': 25.50, 'description': 'Lunch with friends', 'category': 'Food'},
        {'amount': 45.00, 'description': 'Monthly bus pass', 'category': 'Transport'},
        {'amount': 12.99, 'description': 'Netflix subscription', 'category': 'Entertainment'},
        {'amount': 80.00, 'description': 'Electricity bill', 'category': 'Utilities'},
        {'amount': 15.75, 'description': 'Coffee and snacks', 'category': 'Food'},
        {'amount': 30.00, 'description': 'Taxi ride', 'category': 'Transport'},
        {'amount': 25.00, 'description': 'Doctor visit', 'category': 'Healthcare'},
    ]
    
    created_count = 0
    for exp_data in expenses_data:
        category = next(cat for cat in categories if cat.name == exp_data['category'])
        expense, created = Expense.objects.get_or_create(
            user=user,
            amount=exp_data['amount'],
            description=exp_data['description'],
            category=category,
            date=date.today() - timedelta(days=len(expenses_data) - expenses_data.index(exp_data))
        )
        if created:
            created_count += 1
            print(f"✅ Created expense: {exp_data['description']} - ${exp_data['amount']}")
        else:
            print(f"ℹ️ Expense already exists: {exp_data['description']}")
    
    print(f"\n🎉 Sample data creation completed!")
    print(f"📊 Summary:")
    print(f"   - Users: {User.objects.count()}")
    print(f"   - Categories: {Category.objects.count()}")
    print(f"   - Expenses: {Expense.objects.count()}")
    print(f"   - New expenses created: {created_count}")
    
    print(f"\n🔑 Demo credentials: demo/demopass123")
    print(f"🌐 Access your API at: http://127.0.0.1:8000/api/")
    print(f"⚙️ Admin interface: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    create_sample_data()