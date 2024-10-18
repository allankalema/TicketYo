import os
import shutil

# List of apps to clear migrations for
apps = [
    'customers',
    'vendors',
    'events',
    'tickets',
    'payments',
    'notifications',
    'analytics',
    'api',
    'frontend',
    'pos',
    'accounts',
]

# Base directory of your Django project
# Adjust this if your apps are in a different location
base_dir = os.path.dirname(os.path.abspath(__file__))

# Function to delete migration files in each app's migrations folder
def delete_migrations(apps):
    for app in apps:
        migrations_dir = os.path.join(base_dir, app, 'migrations')
        
        # Check if the migrations folder exists
        if os.path.exists(migrations_dir):
            for file_name in os.listdir(migrations_dir):
                # Skip __init__.py
                if file_name == '__init__.py':
                    continue
                file_path = os.path.join(migrations_dir, file_name)
                # Delete file or folder
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print(f"Cleared migrations for {app}")
        else:
            print(f"No migrations folder found for {app}, skipping.")

# Execute the migration clearing
delete_migrations(apps)

print("All specified migrations folders have been cleared.")



