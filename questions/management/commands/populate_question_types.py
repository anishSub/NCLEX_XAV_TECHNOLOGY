from django.core.management.base import BaseCommand
from questions.models import QuestionType


class Command(BaseCommand):
    help = 'Populate initial question types for NCLEX platform'

    def handle(self, *args, **kwargs):
        """Create all supported question types"""
        
        question_types = [
            {
                'code': 'MCQ',
                'display_name': 'Multiple Choice Question',
                'description': 'Standard multiple-choice question with one correct answer. Most common NCLEX question type.'
            },
            {
                'code': 'SATA',
                'display_name': 'Select All That Apply',
                'description': 'Multiple-choice question where multiple answers may be correct. Student must select all correct options.'
            },
            {
                'code': 'DRAG_DROP_RATIONALE',
                'display_name': 'Drag & Drop Rationale',
                'description': 'NGN item type where students drag answers from two wells into a clinical reasoning statement.'
            },
            {
                'code': 'MATRIX_MULTIPLE',
                'display_name': 'Matrix Multiple Response',
                'description': 'Grid-based question where students select multiple cells in a table to match findings with conditions.'
            },
            {
                'code': 'DROPDOWN_RATIONALE',
                'display_name': 'Dropdown Cloze Rationale',
                'description': 'Fill-in-the-blank rationale statement using dropdown menus for each blank.'
            },
            {
                'code': 'HOT_SPOT',
                'display_name': 'Hot Spot',
                'description': 'Image-based question where students click on a specific area of an anatomical diagram or chart.'
            },
            {
                'code': 'HIGHLIGHT_TEXT',
                'display_name': 'Highlight Text',
                'description': 'Students highlight relevant information in medical records, charts, or clinical notes.'
            },
        ]

        created_count = 0
        updated_count = 0
        
        for qt_data in question_types:
            question_type, created = QuestionType.objects.get_or_create(
                code=qt_data['code'],
                defaults={
                    'display_name': qt_data['display_name'],
                    'description': qt_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {question_type.display_name} ({question_type.code})')
                )
            else:
                # Update existing record
                question_type.display_name = qt_data['display_name']
                question_type.description = qt_data['description']
                question_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Updated: {question_type.display_name} ({question_type.code})')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(f'\n✨ Summary: Created {created_count}, Updated {updated_count}')
        )
        self.stdout.write('='*60 + '\n')
        
        # Show all active question types
        self.stdout.write('\n📋 Active Question Types:')
        for qt in QuestionType.objects.filter(is_active=True).order_by('display_name'):
            self.stdout.write(f'  - {qt.display_name} ({qt.code})')
