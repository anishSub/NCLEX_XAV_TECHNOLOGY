
'''docker-compose exec web python manage.py initialize_difficulty

The Item Response Theory (IRT) math requires a non-null difficulty to calculate the Probability of Success ($P$). Without this initialization:Theta Updates: The student's ability estimate ($\theta$) will not move correctly because the difference $(\theta - b)$ would be invalid.Fisher Information: The engine won't be able to calculate $P \times (1-P)$, meaning your Standard Error will never shrink.The Graph: Your Chart.js report would show a flat line instead of the narrowing 95% confidence interval.'''


from django.core.management.base import BaseCommand
from questions.models import Questions

class Command(BaseCommand):
    help = 'Initializes difficulty logits for all questions'

    def handle(self, *args, **kwargs):
        # Target questions with uninitialized logits
        questions = Questions.objects.all()
        count = 0

        for q in questions:
            # Baseline 0.0 is the center of the Rasch Model difficulty scale
            if q.difficulty_logit is None or q.difficulty_logit == 0.0:
                q.difficulty_logit = 0.0
                q.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully initialized {count} questions to 0.0 difficulty.'
        ))