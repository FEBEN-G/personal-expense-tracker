from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum  # ADD THIS IMPORT
from .models import Category, Expense

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class CategorySerializer(serializers.ModelSerializer):
    expense_count = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'expense_count', 'total_expenses', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_expense_count(self, obj):
        return obj.expenses.count()

    def get_total_expenses(self, obj):
        # FIXED: Use django.db.models.Sum instead of serializers.Sum
        total = obj.expenses.aggregate(total=Sum('amount'))['total']
        return total if total else 0

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_name(self, value):
        """Ensure category names are unique per user"""
        user = self.context['request'].user
        if Category.objects.filter(user=user, name__iexact=value).exists():
            raise serializers.ValidationError("You already have a category with this name.")
        return value

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={'does_not_exist': 'Category not found.'}
    )
    
    class Meta:
        model = Expense
        fields = (
            'id', 'amount', 'description', 'date', 
            'category', 'category_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # Verify the category belongs to the user
        category = validated_data['category']
        if category.user != validated_data['user']:
            raise serializers.ValidationError({"category": "You don't have permission to use this category."})
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Verify the category belongs to the user if being updated
        if 'category' in validated_data:
            category = validated_data['category']
            if category.user != self.context['request'].user:
                raise serializers.ValidationError({"category": "You don't have permission to use this category."})
        
        return super().update(instance, validated_data)

    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_date(self, value):
        """Ensure date is not in the future"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value

class ExpenseSummarySerializer(serializers.Serializer):
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_count = serializers.IntegerField()
    average_expense = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='USD')
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    category_breakdown = serializers.JSONField(required=False)

    def to_representation(self, instance):
        """Convert Decimal to string for JSON serialization"""
        data = super().to_representation(instance)
        
        # Convert Decimal to string to avoid JSON serialization issues
        for field in ['total_expenses', 'average_expense']:
            if field in data and data[field] is not None:
                data[field] = str(data[field])
                
        return data