"""
Django management command to add fake businesses with real images and menus
Usage: python manage.py add_fake_businesses
"""
import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.contrib.auth.models import User
from accounts.models import Profile
from loyalty.models import Business, Product, Slider

class Command(BaseCommand):
    help = 'Add fake businesses with real images and menus for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if business already exists',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        self.stdout.write(self.style.SUCCESS('Starting to add fake businesses...'))
        
        # Get or create a superuser for business owners
        superuser, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bonus.local',
                'is_superuser': True,
                'is_staff': True
            }
        )
        # Create profile if it doesn't exist
        profile, _ = Profile.objects.get_or_create(user=superuser)
        if profile.role != Profile.Role.SUPERUSER:
            profile.role = Profile.Role.SUPERUSER
            profile.save()
        
        businesses_data = [
            {
                'name': 'Bella Vista Restaurant',
                'description': 'Authentic Italian fine dining experience in the heart of Berlin. Fresh pasta, wood-fired pizza, and exquisite wines.',
                'address': 'Friedrichstraße 123, 10117 Berlin',
                'phone': '+49 30 12345678',
                'email': 'info@bellavista-berlin.de',
                'website': 'https://bellavista-berlin.de',
                'owner_username': 'bellavista_owner',
                'slider_images': [
                    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
                    'https://images.unsplash.com/photo-1555396273-3677a3db64db?w=800',
                    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800',
                ],
                'menu_items': [
                    {
                        'title': 'Margherita Pizza',
                        'description': 'Classic Italian pizza with fresh mozzarella, tomato sauce, and basil',
                        'price_eur': 12.50,
                        'points_reward': 10,
                        'image_url': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600',
                    },
                    {
                        'title': 'Spaghetti Carbonara',
                        'description': 'Creamy pasta with pancetta, eggs, and parmesan cheese',
                        'price_eur': 15.90,
                        'points_reward': 12,
                        'image_url': 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600',
                    },
                    {
                        'title': 'Caesar Salad',
                        'description': 'Fresh romaine lettuce with caesar dressing, croutons, and parmesan',
                        'price_eur': 9.50,
                        'points_reward': 8,
                        'image_url': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=600',
                    },
                    {
                        'title': 'Tiramisu',
                        'description': 'Traditional Italian dessert with coffee and mascarpone',
                        'price_eur': 7.50,
                        'points_reward': 6,
                        'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600',
                    },
                ],
                'reward_items': [
                    {
                        'title': 'Free Appetizer',
                        'description': 'Choose any appetizer from our menu',
                        'points_reward': 50,
                        'image_url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600',
                    },
                    {
                        'title': 'Free Dessert',
                        'description': 'Complimentary dessert with your meal',
                        'points_reward': 30,
                        'image_url': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600',
                    },
                ],
            },
            {
                'name': 'Coffee House Berlin',
                'description': 'Cozy coffee shop serving premium coffee, fresh pastries, and light meals. Perfect for work or relaxation.',
                'address': 'Prenzlauer Allee 45, 10405 Berlin',
                'phone': '+49 30 98765432',
                'email': 'hello@coffeehouse-berlin.de',
                'website': 'https://coffeehouse-berlin.de',
                'owner_username': 'coffeehouse_owner',
                'slider_images': [
                    'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800',
                    'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800',
                    'https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=800',
                ],
                'menu_items': [
                    {
                        'title': 'Cappuccino',
                        'description': 'Rich espresso with steamed milk and foam',
                        'price_eur': 3.50,
                        'points_reward': 3,
                        'image_url': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=600',
                    },
                    {
                        'title': 'Croissant',
                        'description': 'Freshly baked buttery French croissant',
                        'price_eur': 2.80,
                        'points_reward': 2,
                        'image_url': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600',
                    },
                    {
                        'title': 'Avocado Toast',
                        'description': 'Sourdough bread with smashed avocado, poached egg, and feta',
                        'price_eur': 8.90,
                        'points_reward': 7,
                        'image_url': 'https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=600',
                    },
                    {
                        'title': 'Chocolate Cake',
                        'description': 'Decadent chocolate layer cake with cream frosting',
                        'price_eur': 5.50,
                        'points_reward': 4,
                        'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600',
                    },
                ],
                'reward_items': [
                    {
                        'title': 'Free Coffee',
                        'description': 'Get a free coffee of your choice',
                        'points_reward': 20,
                        'image_url': 'https://images.unsplash.com/photo-1517487881594-2787fef5ebf7?w=600',
                    },
                    {
                        'title': 'Free Pastry',
                        'description': 'Choose any pastry from our selection',
                        'points_reward': 15,
                        'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600',
                    },
                ],
            },
            {
                'name': 'Burger Palace',
                'description': 'Gourmet burgers made with premium ingredients. Hand-cut fries, craft beers, and amazing milkshakes.',
                'address': 'Kurfürstendamm 156, 10709 Berlin',
                'phone': '+49 30 55512345',
                'email': 'info@burgerpalace.de',
                'website': 'https://burgerpalace.de',
                'owner_username': 'burgerpalace_owner',
                'slider_images': [
                    'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=800',
                    'https://images.unsplash.com/photo-1550547660-d9450f859349?w=800',
                    'https://images.unsplash.com/photo-1551782450-17144efb9c50?w=800',
                ],
                'menu_items': [
                    {
                        'title': 'Classic Burger',
                        'description': 'Beef patty, lettuce, tomato, onion, pickles, and special sauce',
                        'price_eur': 11.90,
                        'points_reward': 10,
                        'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600',
                    },
                    {
                        'title': 'Chicken Burger',
                        'description': 'Crispy chicken breast with mayo, lettuce, and tomato',
                        'price_eur': 10.50,
                        'points_reward': 9,
                        'image_url': 'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=600',
                    },
                    {
                        'title': 'French Fries',
                        'description': 'Crispy hand-cut fries with sea salt',
                        'price_eur': 4.50,
                        'points_reward': 4,
                        'image_url': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600',
                    },
                    {
                        'title': 'Chocolate Milkshake',
                        'description': 'Creamy chocolate milkshake with whipped cream',
                        'price_eur': 5.90,
                        'points_reward': 5,
                        'image_url': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=600',
                    },
                ],
                'reward_items': [
                    {
                        'title': 'Free Burger',
                        'description': 'Get a free classic burger',
                        'points_reward': 60,
                        'image_url': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=600',
                    },
                    {
                        'title': 'Free Fries',
                        'description': 'Complimentary fries with any burger',
                        'points_reward': 25,
                        'image_url': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600',
                    },
                ],
            },
            {
                'name': 'Sushi Master',
                'description': 'Authentic Japanese sushi and sashimi. Fresh fish daily, traditional techniques, modern presentation.',
                'address': 'Rosenthaler Straße 40, 10178 Berlin',
                'phone': '+49 30 44455666',
                'email': 'info@sushimaster-berlin.de',
                'website': 'https://sushimaster-berlin.de',
                'owner_username': 'sushimaster_owner',
                'slider_images': [
                    'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=800',
                    'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800',
                    'https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=800',
                ],
                'menu_items': [
                    {
                        'title': 'Salmon Sashimi',
                        'description': 'Fresh salmon slices, 6 pieces',
                        'price_eur': 14.90,
                        'points_reward': 12,
                        'image_url': 'https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=600',
                    },
                    {
                        'title': 'California Roll',
                        'description': 'Crab, avocado, cucumber, 8 pieces',
                        'price_eur': 8.50,
                        'points_reward': 7,
                        'image_url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=600',
                    },
                    {
                        'title': 'Miso Soup',
                        'description': 'Traditional Japanese soup with tofu and seaweed',
                        'price_eur': 4.50,
                        'points_reward': 4,
                        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600',
                    },
                    {
                        'title': 'Edamame',
                        'description': 'Steamed soybeans with sea salt',
                        'price_eur': 5.50,
                        'points_reward': 5,
                        'image_url': 'https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=600',
                    },
                ],
                'reward_items': [
                    {
                        'title': 'Free Sushi Roll',
                        'description': 'Choose any roll from our menu',
                        'points_reward': 40,
                        'image_url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=600',
                    },
                    {
                        'title': 'Free Miso Soup',
                        'description': 'Complimentary miso soup with your order',
                        'points_reward': 20,
                        'image_url': 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600',
                    },
                ],
            },
            {
                'name': 'Sweet Dreams Bakery',
                'description': 'Artisan bakery specializing in fresh bread, pastries, cakes, and desserts. Everything baked daily.',
                'address': 'Kastanienallee 12, 10435 Berlin',
                'phone': '+49 30 77788899',
                'email': 'hello@sweetdreams-bakery.de',
                'website': 'https://sweetdreams-bakery.de',
                'owner_username': 'bakery_owner',
                'slider_images': [
                    'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800',
                    'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=800',
                    'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
                ],
                'menu_items': [
                    {
                        'title': 'Sourdough Bread',
                        'description': 'Freshly baked artisan sourdough loaf',
                        'price_eur': 4.50,
                        'points_reward': 4,
                        'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600',
                    },
                    {
                        'title': 'Chocolate Chip Cookie',
                        'description': 'Large cookie with dark chocolate chips',
                        'price_eur': 2.50,
                        'points_reward': 2,
                        'image_url': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600',
                    },
                    {
                        'title': 'Blueberry Muffin',
                        'description': 'Fresh muffin with blueberries and streusel topping',
                        'price_eur': 3.20,
                        'points_reward': 3,
                        'image_url': 'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=600',
                    },
                    {
                        'title': 'Apple Pie',
                        'description': 'Homemade apple pie with cinnamon',
                        'price_eur': 6.50,
                        'points_reward': 6,
                        'image_url': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=600',
                    },
                ],
                'reward_items': [
                    {
                        'title': 'Free Pastry',
                        'description': 'Choose any pastry from our selection',
                        'points_reward': 30,
                        'image_url': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600',
                    },
                    {
                        'title': 'Free Cookie',
                        'description': 'Get a free cookie with any purchase',
                        'points_reward': 15,
                        'image_url': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600',
                    },
                ],
            },
        ]
        
        def download_image(url):
            """Download image from URL and return as ContentFile"""
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return ContentFile(response.content)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to download image from {url}: {e}'))
                return None
        
        created_count = 0
        
        for biz_data in businesses_data:
            # Get or create owner user
            owner, _ = User.objects.get_or_create(
                username=biz_data['owner_username'],
                defaults={
                    'email': biz_data['email'],
                    'first_name': biz_data['name'].split()[0],
                }
            )
            
            # Set up profile
            profile, _ = Profile.objects.get_or_create(user=owner)
            profile.role = Profile.Role.BUSINESS_OWNER
            profile.phone = biz_data['phone']
            profile.business_name = biz_data['name']
            profile.save()
            
            # Create or get business
            business, created = Business.objects.get_or_create(
                owner=owner,
                name=biz_data['name'],
                defaults={
                    'description': biz_data['description'],
                    'address': biz_data['address'],
                    'phone': biz_data['phone'],
                    'email': biz_data['email'],
                    'email_verified': True,
                    'website': biz_data['website'],
                    'reward_point_cost': 100,
                }
            )
            
            # If business exists and force is True, update it
            if not created and force:
                business.description = biz_data['description']
                business.address = biz_data['address']
                business.phone = biz_data['phone']
                business.email = biz_data['email']
                business.website = biz_data['website']
                business.save()
                created = True  # Treat as created to add products
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created business: {business.name}'))
                
                # Add slider images
                for idx, slider_url in enumerate(biz_data['slider_images']):
                    img_file = download_image(slider_url)
                    if img_file:
                        slider = Slider.objects.create(
                            business=business,
                            store=business.name,
                            address=business.address,
                            description=business.description,
                            is_active=True,
                            order=idx
                        )
                        slider.image.save(f'slider_{business.id}_{idx}.jpg', img_file, save=True)
                        self.stdout.write(f'  Added slider image {idx + 1}')
                
                # Add menu items
                for menu_item in biz_data['menu_items']:
                    img_file = download_image(menu_item['image_url'])
                    product = Product.objects.create(
                        business=business,
                        title=menu_item['title'],
                        description=menu_item['description'],
                        price_cents=int(menu_item['price_eur'] * 100),
                        points_reward=menu_item['points_reward'],
                        is_reward=False,
                        active=True
                    )
                    if img_file:
                        product.image.save(f'{product.id}_{menu_item["title"].replace(" ", "_")}.jpg', img_file, save=True)
                    self.stdout.write(f'  Added menu item: {menu_item["title"]}')
                
                # Add reward items
                for reward_item in biz_data['reward_items']:
                    img_file = download_image(reward_item['image_url'])
                    product = Product.objects.create(
                        business=business,
                        title=reward_item['title'],
                        description=reward_item['description'],
                        price_cents=0,
                        points_reward=reward_item['points_reward'],
                        is_reward=True,
                        active=True
                    )
                    if img_file:
                        product.image.save(f'{product.id}_{reward_item["title"].replace(" ", "_")}.jpg', img_file, save=True)
                    self.stdout.write(f'  Added reward item: {reward_item["title"]}')
            else:
                self.stdout.write(self.style.WARNING(f'Business already exists: {business.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} new businesses!'))
        self.stdout.write(self.style.SUCCESS('You can delete them later from the admin panel.'))

