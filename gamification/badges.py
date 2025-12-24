"""
Badge definitions with Himalayan theme - Simple and Cool!
Each badge has a unique code, name, icon, and points.
"""

BADGE_DEFINITIONS = {
    # ========== STREAK BADGES (Himalayan Theme!) ==========
    'BASE_CAMP': {
        'name_nepali': 'Base Camp',
        'name_english': 'First Step',
        'icon': '🏕️',
        'description': 'Welcome to your NCLEX journey!',
        'points': 10,
        'category': 'streak',
        'condition': lambda profile, _: profile.current_streak >= 1
    },
    
    'TRAIL_BLAZER': {
        'name_nepali': 'Trail Blazer',
        'name_english': 'Consistent',
        'icon': '🥾',
        'description': '3-day login streak',
        'points': 50,
        'category': 'streak',
        'condition': lambda profile, _: profile.current_streak >= 3
    },
    
    'SUMMIT_PUSH': {
        'name_nepali': 'Summit Push',
        'name_english': 'Dedicated',
        'icon': '⛰️',
        'description': '7-day login streak',
        'points': 100,
        'category': 'streak',
        'condition': lambda profile, _: profile.current_streak >= 7
    },
    
    'ANNAPURNA': {
        'name_nepali': 'Annapurna',
        'name_english': 'Mountain Climber',
        'icon': '🏔️',
        'description': '30-day login streak - Legendary!',
        'points': 300,
        'category': 'streak',
        'condition': lambda profile, _: profile.current_streak >= 30
    },
    
    'EVEREST': {
        'name_nepali': 'Everest',
        'name_english': 'Top of the World',
        'icon': '🗻',
        'description': '100-day login streak - Ultimate Champion!',
        'points': 1000,
        'category': 'streak',
        'condition': lambda profile, _: profile.current_streak >= 100
    },
    
    # ========== QUESTION BADGES ==========
    'EXPLORER': {
        'name_nepali': 'Explorer',
        'name_english': 'Question Starter',
        'icon': '🔍',
        'description': 'Answered 50 questions',
        'points': 50,
        'category': 'questions',
        'condition': lambda profile, _: profile.total_questions_answered >= 50
    },
    
    'CLIMBER': {
        'name_nepali': 'Climber',
        'name_english': 'Making Progress',
        'icon': '🧗',
        'description': 'Answered 100 questions',
        'points': 100,
        'category': 'questions',
        'condition': lambda profile, _: profile.total_questions_answered >= 100
    },
    
    'SHERPA': {
        'name_nepali': 'Sherpa',
        'name_english': 'Guide',
        'icon': '💪',
        'description': 'Answered 500 questions',
        'points': 300,
        'category': 'questions',
        'condition': lambda profile, _: profile.total_questions_answered >= 500
    },
    
    'PEAK_MASTER': {
        'name_nepali': 'Peak Master',
        'name_english': 'Expert',
        'icon': '👑',
        'description': 'Answered 1000 questions',
        'points': 500,
        'category': 'questions',
        'condition': lambda profile, _: profile.total_questions_answered >= 1000
    },
    
    'SAGARMATHA': {
        'name_nepali': 'Sagarmatha',
        'name_english': 'Everest Legend',
        'icon': '🌟',
        'description': 'Answered 5000 questions - Ultimate dedication!',
        'points': 2000,
        'category': 'questions',
        'condition': lambda profile, _: profile.total_questions_answered >= 5000
    },
    
    # ========== PERFORMANCE BADGES ==========
    'RISING_STAR': {
        'name_nepali': 'Rising Star',
        'name_english': 'Good Student',
        'icon': '⭐',
        'description': '70% average score',
        'points': 100,
        'category': 'performance',
        'condition': lambda profile, _: profile.average_score >= 70 and profile.total_questions_answered >= 50
    },
    
    'SUMMIT_VIEW': {
        'name_nepali': 'Summit View',
        'name_english': 'Excellent',
        'icon': '🌄',
        'description': '80% average score',
        'points': 200,
        'category': 'performance',
        'condition': lambda profile, _: profile.average_score >= 80 and profile.total_questions_answered >= 100
    },
    
    'PEAK_POWER': {
        'name_nepali': 'Peak Power',
        'name_english': 'Outstanding',
        'icon': '💫',
        'description': '90% average score - Incredible!',
        'points': 500,
        'category': 'performance',
        'condition': lambda profile, _: profile.average_score >= 90 and profile.total_questions_answered >= 200
    },
    
    'EVEREST_LEVEL': {
        'name_nepali': 'Everest Level',
        'name_english': 'Nearly Perfect',
        'icon': '✨',
        'description': '95% average score - You\'re amazing!',
        'points': 1000,
        'category': 'performance',
        'condition': lambda profile, _: profile.average_score >= 95 and profile.total_questions_answered >= 500
    },
    
    # ========== SPECIAL BADGES ==========
    'GURKHA': {
        'name_nepali': 'Gurkha Warrior',
        'name_english': 'Brave Fighter',
        'icon': '⚔️',
        'description': 'Complete 10 full practice exams',
        'points': 500,
        'category': 'special',
        'condition': lambda profile, _: False  # Requires special tracking
    },
    
    'YETI': {
        'name_nepali': 'Yeti',
        'name_english': 'Legendary',
        'icon': '🦍',
        'description': 'Perfect score on CAT exam',
        'points': 1000,
        'category': 'special',
        'condition': lambda profile, _: False  # Requires special tracking
    },
    
    'BUDDHA_MIND': {
        'name_nepali': 'Buddha Mind',
        'name_english': 'Enlightened',
        'icon': '🧘',
        'description': 'Master all 8 categories',
        'points': 800,
        'category': 'special',
        'condition': lambda profile, _: False  # Requires special tracking
    },
}


def get_badge_info(badge_code):
    """Get badge information by code"""
    return BADGE_DEFINITIONS.get(badge_code, None)


def get_badges_by_category(category):
    """Get all badges in a specific category"""
    return {code: badge for code, badge in BADGE_DEFINITIONS.items() 
            if badge['category'] == category}


def get_all_badge_codes():
    """Get list of all badge codes"""
    return list(BADGE_DEFINITIONS.keys())
