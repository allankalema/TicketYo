from django.contrib import admin
from django.utils.html import format_html
from .models import Event, TicketCategory, ActionLog  

# Define the inline for TicketCategory
class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1  # Adds one extra blank form to the inline in the admin

class ActionLogAdmin(admin.ModelAdmin):  # Custom ModelAdmin for ActionLog
    list_display = ('admin_user', 'event', 'action', 'timestamp')  # Fields to display in the table
    readonly_fields = ('admin_user', 'event', 'action', 'timestamp')  # Make these fields read-only
    search_fields = ('admin_user__username', 'event__title', 'action')  # Searchable fields

    def has_add_permission(self, request):
        return False  # Disable adding new ActionLog entries

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing existing ActionLog entries

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting ActionLog entries

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'start_date', 'end_date', 'tickets_available', 'regular_price', 'sale_price', 'status', 'adminaction')
    list_filter = ('category', 'start_date', 'end_date', 'adminaction')
    search_fields = ('title', 'description', 'venue_name', 'vendor__storename')
    inlines = [TicketCategoryInline]  # Keep the TicketCategory inline

    actions = ['approve_event', 'reject_event']

    # Bulk approval action
    def approve_event(self, request, queryset):
        for event in queryset:
            if event.status == 'pending':
                event.status = 'approved'
                event.adminaction = request.user
                event.save()
                ActionLog.objects.create(admin_user=request.user, event=event, action=f'approved by {request.user.username}')
        self.message_user(request, "Selected events have been approved.")

    # Bulk rejection action
    def reject_event(self, request, queryset):
        for event in queryset:
            if event.status == 'pending':
                event.status = 'rejected'
                event.adminaction = request.user
                event.save()
                ActionLog.objects.create(admin_user=request.user, event=event, action=f'rejected by {request.user.username}')
        self.message_user(request, "Selected events have been rejected.")

    approve_event.short_description = 'Approve selected events'
    reject_event.short_description = 'Reject selected events'

    # Overriding the save_model method to log changes
    def save_model(self, request, obj, form, change):
        if change:  # This means the object is being updated
            # Compare old and new values
            old_values = Event.objects.get(pk=obj.pk)
            changes = []
            
            # Check for changes and log them
            if old_values.title != obj.title:
                changes.append(f"Title changed from '{old_values.title}' to '{obj.title}'")
            if old_values.status != obj.status:
                changes.append(f"Status changed from '{old_values.status}' to '{obj.status}'")
            if old_values.start_date != obj.start_date:
                changes.append(f"Start date changed from '{old_values.start_date}' to '{obj.start_date}'")
            if old_values.end_date != obj.end_date:
                changes.append(f"End date changed from '{old_values.end_date}' to '{obj.end_date}'")
            if old_values.venue_name != obj.venue_name:
                changes.append(f"Venue name changed from '{old_values.venue_name}' to '{obj.venue_name}'")
            # Add more fields as necessary
            
            # Create a log entry with detailed changes
            if changes:
                action_description = "; ".join(changes)
                ActionLog.objects.create(
                    admin_user=request.user,
                    event=obj,
                    action=f'Updated: {action_description}'  # Detailed log entry
                )

        # Call the parent method to save the model
        super().save_model(request, obj, form, change)

# Register the models with the admin site
admin.site.register(Event, EventAdmin)
admin.site.register(TicketCategory)
admin.site.register(ActionLog, ActionLogAdmin)  # Register ActionLog with custom ModelAdmin
