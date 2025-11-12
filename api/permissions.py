from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_permission(self, request, view):
        # Allow list/create if authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the object belongs to the requesting user
        return obj.user == request.user


class IsCategoryOwner(permissions.BasePermission):
    """
    Custom permission to only allow category owners to access it.
    """
    
    def has_permission(self, request, view):
        # Allow list/create if authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the category belongs to the requesting user
        return obj.user == request.user


class IsObjectOwner(permissions.BasePermission):
    """
    Generic permission to check if user owns the object.
    Can be used for any model with a 'user' field.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit objects, but anyone can view.
    Useful for public data that only owners can modify.
    """
    
    def has_permission(self, request, view):
        # Allow all users to view (read-only)
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsStaffOrOwner(permissions.BasePermission):
    """
    Custom permission to allow staff users or owners to access objects.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Staff users can access any object
        if request.user.is_staff:
            return True
            
        # Regular users can only access their own objects
        return obj.user == request.user