from django.http import HttpResponseForbidden
from django.shortcuts import render
from functools import wraps

def restrict_pos_agents(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_posagent:
            # Show 403 error page with custom message
            context = {
                'error_message': "As a POS agent, you are only allowed to access events you are assigned to."
            }
            return render(request, '403.html', context, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
