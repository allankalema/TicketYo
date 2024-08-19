import os
base_dir = 'static'

# List of directories to create under the templates folder
directories = [
    'customers',
    'vendors',
    'events',
    'tickets',
    'payments',
    'notifications',
    'analytics',
    'api'
]

# Create the base directory if it doesn't exist
os.makedirs(base_dir, exist_ok=True)

# Create each subdirectory
for directory in directories:
    dir_path = os.path.join(base_dir, directory)
    os.makedirs(dir_path, exist_ok=True)

print("All directories created successfully.")
