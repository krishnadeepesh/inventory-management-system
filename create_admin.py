from core.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin', role='ADMIN')
    print('Admin user created.')
else:
    print('Admin user already exists.')
