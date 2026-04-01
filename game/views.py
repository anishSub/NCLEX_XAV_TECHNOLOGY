from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from questions.models import Questions
from categories.models import Categories
import random


def game_page(request):
    """Display the game information page"""
    return render(request, 'game/game_page.html')


@login_required
def play_game(request):
    """Play the game in browser with Phaser.js"""
    return render(request, 'game/play_game_phaser.html')


# NOTE: No @login_required — AJAX calls need JSON back, not a 302 redirect.
# Authentication is enforced by returning 401 JSON rather than redirecting.
def get_categories_api(request):
    """API endpoint to get all categories with question counts."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    categories = list(Categories.objects.all().values('id', 'name'))

    # Annotate each category with count of GAME-COMPATIBLE (list-format) questions
    for cat in categories:
        qs = Questions.objects.filter(category_ids__id=cat['id'])
        valid_count = sum(
            1 for q in qs.values('options')
            if isinstance(q['options'], list) and len(q['options']) >= 2
        )
        cat['question_count'] = valid_count

    return JsonResponse(categories, safe=False)


def get_questions_api(request):
    """API endpoint to get random questions for a category (game-compatible format only)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required', 'questions': []}, status=401)

    category_id = request.GET.get('category')
    limit = int(request.GET.get('limit', 10))

    try:
        if category_id:
            raw_qs = list(Questions.objects.filter(
                category_ids__id=category_id
            ).values('id', 'text', 'options', 'correct_option_ids', 'type'))
        else:
            raw_qs = list(Questions.objects.all().values(
                'id', 'text', 'options', 'correct_option_ids', 'type'
            ))
    except Exception as e:
        return JsonResponse({'error': str(e), 'questions': []}, status=500)

    # Keep only MCQ-style questions: options must be a list of 2+ items
    valid_questions = [
        q for q in raw_qs
        if isinstance(q['options'], list) and len(q['options']) >= 2
    ]

    # Shuffle and limit
    random.shuffle(valid_questions)
    valid_questions = valid_questions[:limit]

    labels = ['A', 'B', 'C', 'D']
    formatted_questions = []

    for q in valid_questions:
        options_list = q['options']

        # Normalise each option to a plain string
        if isinstance(options_list[0], dict):
            # Format: [{'id': 'A', 'text': '...'}, ...]
            option_texts = [opt.get('text', str(opt.get('id', ''))) for opt in options_list[:4]]
        else:
            # Format: ['option1', 'option2', ...]
            option_texts = [str(o) for o in options_list[:4]]

        # Pad to exactly 4 options
        while len(option_texts) < 4:
            option_texts.append('—')

        # ── Resolve correct answer to a letter (A/B/C/D) ──────────────────
        correct_ids = q['correct_option_ids']
        correct_answer = 'A'  # safe fallback

        if isinstance(correct_ids, list) and correct_ids:
            first = correct_ids[0]
            if isinstance(first, str):
                if first.upper() in labels:
                    # Stored as letter 'B'
                    correct_answer = first.upper()
                else:
                    # Stored as option text — find its index
                    try:
                        idx = option_texts.index(first)
                        correct_answer = labels[idx]
                    except ValueError:
                        correct_answer = 'A'
            elif isinstance(first, int):
                # Stored as 0-based index
                correct_answer = labels[first] if 0 <= first < 4 else 'A'

        elif isinstance(correct_ids, str) and correct_ids.upper() in labels:
            correct_answer = correct_ids.upper()

        formatted_questions.append({
            'id': q['id'],
            'text': q['text'],
            'options': option_texts,
            'correct_answer': correct_answer,
            'type': q['type']
        })

    return JsonResponse({'questions': formatted_questions, 'total': len(formatted_questions)})
