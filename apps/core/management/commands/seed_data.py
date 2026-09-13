"""
Management command: seed_data
Usage: python manage.py seed_data

Creates initial service categories, skills, and sample provider profiles.
This is idempotent — safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.providers.models import ServiceCategory, Skill, ProviderProfile, ServiceArea, Availability

User = get_user_model()


CATEGORIES = [
    {
        'name': 'Plumber',
        'slug': 'plumber',
        'icon': '🔧',
        'description': 'Professional plumbing services including pipe repair, leak fixing, drain cleaning, and fixture installation.',
        'common_problems': 'leaking pipe, blocked drain, tap dripping, toilet flush issue, water heater leak, low water pressure',
        'keywords': 'leak, pipe, drain, tap, faucet, sink, toilet, water, sewage, blockage, plumbing',
        'skills': [
            'Pipe Repair & Replacement', 'Leak Detection & Fixing', 'Drain Cleaning & Unblocking',
            'Tap & Faucet Repair', 'Toilet Flush Repair', 'Geyser/Water Heater Repair',
            'Water Pressure Fixing', 'Pipe Fitting & Installation', 'Sewer Line Repair',
        ],
    },
    {
        'name': 'Electrician',
        'slug': 'electrician',
        'icon': '⚡',
        'description': 'Licensed electrical services for wiring, repairs, and installations in residential buildings.',
        'common_problems': 'power tripping, switch not working, sparking socket, fan slow, wiring repair',
        'keywords': 'electric, wiring, switch, socket, breaker, fan, power, light, fuse, spark, trip',
        'skills': [
            'Wiring Repair & Installation', 'Switch & Socket Repair', 'MCB/Breaker Installation',
            'Fan Installation & Repair', 'Load Balancing', 'Short Circuit Fixing',
            'AC Wiring', 'Generator Connection', 'UPS/Inverter Installation',
            'New Point Installation',
        ],
    },
    {
        'name': 'AC Technician',
        'slug': 'ac-technician',
        'icon': '❄️',
        'description': 'Expert air conditioning installation, maintenance, and repair for all AC types.',
        'common_problems': 'AC not cooling, AC noisy, gas leaking, compressor not starting, water dripping',
        'keywords': 'ac, air conditioner, cooling, refrigerant, compressor, filter, hvac, split unit',
        'skills': [
            'AC Gas Charging/Recharging', 'Compressor Repair & Replacement', 'Filter Cleaning',
            'PCB/Board Diagnosis', 'Split Unit Installation', 'AC Drain Pipe Cleaning',
            'Condenser Coil Cleaning', 'Thermostat/Remote Repair', 'Annual AC Servicing',
        ],
    },
    {
        'name': 'Carpenter',
        'slug': 'carpenter',
        'icon': '🪵',
        'description': 'Skilled carpentry for furniture, doors, windows, cabinets, and wooden flooring.',
        'common_problems': 'door not closing, furniture repair, cabinet broken, window frame repair',
        'keywords': 'wood, door, window, cabinet, furniture, wardrobe, shelf, flooring, ceiling, carpenter',
        'skills': [
            'Door Fitting & Repair', 'Furniture Repair & Polish', 'Cabinet Installation',
            'Window Frame Repair', 'False Ceiling Installation', 'Wooden Flooring',
            'Lock & Handle Installation', 'Sliding Door Repair', 'Custom Furniture Making',
        ],
    },
    {
        'name': 'Painter',
        'slug': 'painter',
        'icon': '🎨',
        'description': 'Interior and exterior painting, wall texture, waterproofing, and wood polish.',
        'common_problems': 'wall paint peeling, seepage on wall, need house painted, wood polishing',
        'keywords': 'paint, wall, ceiling, color, brush, whitewash, plaster, seepage, waterproof',
        'skills': [
            'Interior Wall Painting', 'Exterior House Painting', 'Texture & Design Painting',
            'Wall Seepage Treatment', 'Waterproofing', 'Wood Polish & Varnish',
            'Plaster Repair', 'Roof Treatment',
        ],
    },
    {
        'name': 'Appliance Repair',
        'slug': 'appliance-repair',
        'icon': '🫙',
        'description': 'Repair services for all major household appliances including washing machines, refrigerators, and geysers.',
        'common_problems': 'washing machine not working, fridge not cooling, geyser not heating, oven repair',
        'keywords': 'washing machine, refrigerator, fridge, geyser, oven, microwave, appliance, motor',
        'skills': [
            'Washing Machine Repair', 'Refrigerator/Fridge Repair', 'Geyser Repair',
            'Microwave Oven Repair', 'Electric Oven Repair', 'Water Pump Repair',
            'Motor Rewinding', 'PCB Diagnosis', 'UPS & Battery Repair',
        ],
    },
    {
        'name': 'Cleaning Service',
        'slug': 'cleaning-service',
        'icon': '🧹',
        'description': 'Professional deep cleaning, sofa shampooing, water tank cleaning, and pest control.',
        'common_problems': 'house dirty, sofa cleaning, water tank cleaning, pest control needed',
        'keywords': 'clean, cleaning, sofa, carpet, tank, pest, cockroach, deep clean, sanitize',
        'skills': [
            'Deep House Cleaning', 'Sofa & Carpet Shampooing', 'Water Tank Cleaning',
            'Kitchen Deep Cleaning', 'Post-Construction Cleaning', 'Pest Control',
            'Mattress Cleaning', 'Office Cleaning',
        ],
    },
    {
        'name': 'Mason / Civil Work',
        'slug': 'mason',
        'icon': '🧱',
        'description': 'Masonry and civil work including wall repair, tile fitting, and construction.',
        'common_problems': 'wall crack, tile broken, cement work, bathroom tiles falling',
        'keywords': 'wall, cement, tiles, masonry, brick, plaster, crack, construction, bathroom',
        'skills': [
            'Wall Repair & Plastering', 'Tile Fitting', 'Brick Laying',
            'Floor Tile Installation', 'Bathroom Renovation', 'Crack Repair',
        ],
    },
]


SAMPLE_PROVIDERS = [
    {
        'username': 'ahmed_plumbing',
        'first_name': 'Ahmed', 'last_name': 'Khan',
        'email': 'ahmed@example.com',
        'business_name': 'Ahmed Plumbing Services',
        'category_slug': 'plumber',
        'bio': 'Experienced plumber serving Rawalpindi and Islamabad for over 6 years. Specializing in leak repair and pipe fitting.',
        'experience_years': 6,
        'base_location': 'Bahria Town Rawalpindi',
        'service_areas': ['Bahria Phase 1', 'Bahria Phase 2', 'Bahria Phase 3', 'Bahria Phase 4', 'Bahria Phase 5'],
        'skills': ['Pipe Repair & Replacement', 'Leak Detection & Fixing', 'Drain Cleaning & Unblocking', 'Tap & Faucet Repair'],
        'average_rating': 4.8, 'total_reviews': 47,
        'min_charge': 1000, 'max_charge': 5000,
        'phone_number': '0300-1234567',
    },
    {
        'username': 'hassan_plumbing',
        'first_name': 'Hassan', 'last_name': 'Raza',
        'email': 'hassan@example.com',
        'business_name': 'Hassan Plumbing Services',
        'category_slug': 'plumber',
        'bio': 'Professional plumber with 5 years experience. Available 7 days a week for emergency repairs.',
        'experience_years': 5,
        'base_location': 'Rawalpindi',
        'service_areas': ['Saddar Rawalpindi', 'Commercial Market', 'Raja Bazaar', 'Satellite Town'],
        'skills': ['Drain Cleaning & Unblocking', 'Toilet Flush Repair', 'Geyser/Water Heater Repair', 'Sewer Line Repair'],
        'average_rating': 4.6, 'total_reviews': 32,
        'min_charge': 800, 'max_charge': 4000,
        'phone_number': '0311-9876543',
    },
    {
        'username': 'ali_electric',
        'first_name': 'Ali', 'last_name': 'Hassan',
        'email': 'ali_electric@example.com',
        'business_name': 'Ali Electric Services',
        'category_slug': 'electrician',
        'bio': 'Licensed electrician with 7 years of experience. Expert in home wiring, MCB installation, and fan repair.',
        'experience_years': 7,
        'base_location': 'Bahria Town Rawalpindi',
        'service_areas': ['Bahria Phase 1', 'Bahria Phase 2', 'Bahria Phase 6', 'Bahria Phase 7', 'Bahria Phase 8'],
        'skills': ['Wiring Repair & Installation', 'Switch & Socket Repair', 'MCB/Breaker Installation', 'Fan Installation & Repair', 'AC Wiring'],
        'average_rating': 4.7, 'total_reviews': 58,
        'min_charge': 1500, 'max_charge': 8000,
        'phone_number': '0333-5554444',
    },
    {
        'username': 'city_electric',
        'first_name': 'Usman', 'last_name': 'Malik',
        'email': 'usman@example.com',
        'business_name': 'City Electric Works',
        'category_slug': 'electrician',
        'bio': 'Professional electrical contractor offering full wiring, renovation, and repair services in Islamabad and Rawalpindi.',
        'experience_years': 10,
        'base_location': 'G-11 Islamabad',
        'service_areas': ['G-10 Islamabad', 'G-11 Islamabad', 'G-13 Islamabad', 'I-8 Islamabad', 'I-10 Islamabad'],
        'skills': ['Wiring Repair & Installation', 'Load Balancing', 'Generator Connection', 'UPS/Inverter Installation', 'Short Circuit Fixing'],
        'average_rating': 4.5, 'total_reviews': 41,
        'min_charge': 2000, 'max_charge': 15000,
        'phone_number': '0321-1112222',
    },
    {
        'username': 'cool_tech_ac',
        'first_name': 'Bilal', 'last_name': 'Ahmed',
        'email': 'bilal_ac@example.com',
        'business_name': 'CoolTech AC Services',
        'category_slug': 'ac-technician',
        'bio': 'Certified AC technician specializing in all brands. Expert in gas charging, compressor repair, and annual servicing.',
        'experience_years': 8,
        'base_location': 'Bahria Town Rawalpindi',
        'service_areas': ['Bahria Phase 1', 'Bahria Phase 2', 'Bahria Phase 3', 'Bahria Phase 4', 'DHA Rawalpindi'],
        'skills': ['AC Gas Charging/Recharging', 'Compressor Repair & Replacement', 'Filter Cleaning', 'Split Unit Installation', 'PCB/Board Diagnosis'],
        'average_rating': 4.9, 'total_reviews': 73,
        'min_charge': 1500, 'max_charge': 12000,
        'phone_number': '0345-6667777',
    },
    {
        'username': 'master_carpenter',
        'first_name': 'Saeed', 'last_name': 'Ahmad',
        'email': 'saeed@example.com',
        'business_name': 'Master Carpentry Works',
        'category_slug': 'carpenter',
        'bio': 'Skilled carpenter with 12 years of experience. Specializing in furniture repair, door fitting, and cabinet making.',
        'experience_years': 12,
        'base_location': 'Rawalpindi',
        'service_areas': ['Rawalpindi', 'Islamabad', 'Bahria Town', 'DHA'],
        'skills': ['Door Fitting & Repair', 'Furniture Repair & Polish', 'Cabinet Installation', 'False Ceiling Installation'],
        'average_rating': 4.6, 'total_reviews': 29,
        'min_charge': 1000, 'max_charge': 20000,
        'phone_number': '0300-8889999',
    },
    {
        'username': 'home_cleaners',
        'first_name': 'Tariq', 'last_name': 'Mehmood',
        'email': 'tariq@example.com',
        'business_name': 'Home Clean Pro',
        'category_slug': 'cleaning-service',
        'bio': 'Professional cleaning team offering deep cleaning, sofa shampooing, and water tank cleaning services.',
        'experience_years': 4,
        'base_location': 'Islamabad',
        'service_areas': ['F-6 Islamabad', 'F-7 Islamabad', 'F-8 Islamabad', 'G-8 Islamabad', 'G-9 Islamabad'],
        'skills': ['Deep House Cleaning', 'Sofa & Carpet Shampooing', 'Water Tank Cleaning', 'Pest Control'],
        'average_rating': 4.4, 'total_reviews': 21,
        'min_charge': 2000, 'max_charge': 10000,
        'phone_number': '0316-1234321',
    },
    {
        'username': 'appliance_king',
        'first_name': 'Naveed', 'last_name': 'Shah',
        'email': 'naveed@example.com',
        'business_name': 'Appliance King Repair',
        'category_slug': 'appliance-repair',
        'bio': 'Expert appliance technician with 9 years experience. Repairing all major brands of washing machines, refrigerators, and geysers.',
        'experience_years': 9,
        'base_location': 'Rawalpindi',
        'service_areas': ['Rawalpindi', 'Islamabad', 'Bahria Town', 'Chaklala'],
        'skills': ['Washing Machine Repair', 'Refrigerator/Fridge Repair', 'Geyser Repair', 'Motor Rewinding'],
        'average_rating': 4.7, 'total_reviews': 62,
        'min_charge': 1000, 'max_charge': 8000,
        'phone_number': '0333-4443333',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with initial service categories, skills, and sample providers.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('==> Seeding Database'))
        self.stdout.write('-' * 60)

        # Create categories and skills
        for cat_data in CATEGORIES:
            skills_data = cat_data.pop('skills')
            category, created = ServiceCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"  {action} category: {category.name}")

            for skill_name in skills_data:
                Skill.objects.get_or_create(name=skill_name, category=category)

        self.stdout.write(f'\n[OK] {ServiceCategory.objects.count()} categories with skills created')

        # Create sample providers
        self.stdout.write('\n[+] Creating sample provider profiles...')
        created_count = 0

        for p_data in SAMPLE_PROVIDERS:
            username = p_data.pop('username')
            category_slug = p_data.pop('category_slug')
            service_areas = p_data.pop('service_areas')
            skills_list = p_data.pop('skills')
            average_rating = p_data.pop('average_rating')
            total_reviews = p_data.pop('total_reviews')

            # Create user
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': p_data.pop('first_name'),
                    'last_name': p_data.pop('last_name'),
                    'email': p_data.pop('email'),
                    'role': 'PROVIDER',
                }
            )
            if user_created:
                user.set_password('provider123')
                user.save()

            # Get category
            try:
                category = ServiceCategory.objects.get(slug=category_slug)
            except ServiceCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Category '{category_slug}' not found, skipping"))
                continue

            # Create or update provider profile
            profile, _ = ProviderProfile.objects.update_or_create(
                user=user,
                defaults={
                    'category': category,
                    'average_rating': average_rating,
                    'total_reviews': total_reviews,
                    'is_verified': True,
                    'is_available': True,
                    **p_data,
                }
            )

            # Add service areas
            for area_name in service_areas:
                ServiceArea.objects.get_or_create(
                    provider=profile,
                    area_name=area_name,
                    defaults={'city': 'Rawalpindi' if 'Bahria' in area_name or 'Rawalpindi' in area_name else 'Islamabad'}
                )

            # Add skills
            for skill_name in skills_list:
                try:
                    skill = Skill.objects.get(name=skill_name, category=category)
                    profile.skills.add(skill)
                except Skill.DoesNotExist:
                    pass

            created_count += 1
            self.stdout.write(f"  [OK] {profile.business_name}")

        self.stdout.write('\n' + '-' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'\nSeed data complete!\n'
            f'   Categories: {ServiceCategory.objects.count()}\n'
            f'   Providers: {ProviderProfile.objects.count()} ({ProviderProfile.objects.filter(is_verified=True).count()} verified)\n'
        ))

        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='ADMIN',
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin / admin123')
            )
