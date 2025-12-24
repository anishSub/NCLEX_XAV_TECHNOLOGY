from django.core.management.base import BaseCommand
from categories.models import Categories


class Command(BaseCommand):
    help = 'Populate standard NCLEX-RN categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Management of Care', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Safety and Infection Control', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Health Promotion and Maintenance', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Psychosocial Integrity', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Basic Care and Comfort', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Pharmacological and Parenteral Therapies', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Reduction of Risk Potential', 'type': 'NCLEX_CATEGORY'},
            {'name': 'Physiological Adaptation', 'type': 'NCLEX_CATEGORY'},
        ]

        created_count = 0
        for cat_data in categories:
            category, created = Categories.objects.get_or_create(
                name=cat_data['name'],
                defaults={'type': cat_data['type']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Completed! {created_count} categories created.')
        )
