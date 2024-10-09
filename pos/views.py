from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from vendors.models import Vendor  # Assuming you have a Vendor model

@login_required
def manage_pos_agents(request):
    vendor = Vendor.objects.get(username=request.user.username)
    
    # This context will pass information for rendering (empty for now)
    context = {
        'vendor': vendor,
        'active_agents': [],  # Empty for now
        'inactive_agents': []  # Empty for now
    }
    
    return render(request, 'pos/manage_agents.html', context)
