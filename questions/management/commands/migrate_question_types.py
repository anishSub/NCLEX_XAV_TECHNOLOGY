from django.core.management.base import BaseCommand
from questions.models import Questions, QuestionType


class Command(BaseCommand):
    help = 'Migrate existing questions to use QuestionType ForeignKey'

    def handle(self, *args, **kwargs):
        """Migrate all existing questions from type CharField to question_type ForeignKey"""
        
        # Get all questions that don't have question_type set
        questions_to_migrate = Questions.objects.filter(question_type__isnull=True)
        total_count = questions_to_migrate.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ No questions need migration. All questions already use question_type field!\n'))
            return
        
        self.stdout.write(f'\n🔄 Found {total_count} questions to migrate...\n')
        
        migrated_count = 0
        error_count = 0
        type_stats = {}
        
        for question in questions_to_migrate:
            try:
                # Look up QuestionType by code from old type field
                if question.type:
                    try:
                        question_type = QuestionType.objects.get(code=question.type)
                        question.question_type = question_type
                        question.save()
                        
                        migrated_count += 1
                        type_stats[question.type] = type_stats.get(question.type, 0) + 1
                        
                        if migrated_count % 10 == 0:
                            self.stdout.write(f'  ✓ Migrated {migrated_count}/{total_count}...')
                    
                    except QuestionType.DoesNotExist:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Question ID {question.id}: QuestionType "{question.type}" not found')
                        )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Question ID {question.id}: No type specified')
                    )
            
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Question ID {question.id}: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\n✨ Migration Complete!'))
        self.stdout.write(f'  ✅ Successfully migrated: {migrated_count}')
        self.stdout.write(f'  ❌ Errors: {error_count}')
        self.stdout.write('='*60 + '\n')
        
        if type_stats:
            self.stdout.write('\n📊 Migration Breakdown by Type:')
            for type_code, count in sorted(type_stats.items()):
                self.stdout.write(f'  - {type_code}: {count} questions')
            self.stdout.write('')
