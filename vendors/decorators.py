from django.core.exceptions import PermissionDenied

def vendor_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a vendor,
    raises a PermissionDenied error if not.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not allowed to access this page.")  # Return Permission Denied error
    return _wrapped_view
