from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-3^0&6)j-dclz4(nfu&3j8(hrin#*t1gprc$v(@+x2stu2h%q76'
DEBUG = True
ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your Apps
    "users",
    "categories",
    "scenarios",
    "questions",
    "exam_sessions",
    "user_responses",
    "pages",
    "study_planner",  # NEW: Study Planner with calendar and to-do list
    "subscriptions",  # NEW: Subscription & Payment System
    "gamification",   # NEW: Gamification System (Streaks, Badges, Points)
    
    # ALLAUTH (Social Login)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',   # Google
    'allauth.socialaccount.providers.facebook', # Facebook
    
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    #  specifically for Allauth:
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'nclex_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add templates directory for admin overrides
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nclex_core.wsgi.application'

STATIC_URL = 'static/'

# Global static folder (for theme.css, theme-toggle.js, etc.)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# This is where files go when you run "python manage.py collectstatic" (for production)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nclex_db',
        'USER': 'nclex_user',
        'PASSWORD': 'nclex_password',
        # IF 'DB_HOST' is set (by Docker), use it. OTHERWISE use '127.0.0.1' (your Mac).
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'), 
        # IF 'DB_PORT' is set (by Docker), use 5432. OTHERWISE use '5433' (your Mac).
        'PORT': os.environ.get('DB_PORT', '5433'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

AUTH_USER_MODEL = 'users.Users'
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Ensure these match your actual URL names
LOGIN_REDIRECT_URL = 'home' 
LOGOUT_REDIRECT_URL = 'login'


# --- AUTHENTICATION BACKENDS ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Needed for Admin login
    'allauth.account.auth_backends.AuthenticationBackend', # Needed for Google/Facebook
]

# --- ALLAUTH CONFIGURATION ---
SITE_ID = 1  # Required by allauth

# Login Settings
# Login Settings (NEW - USE THIS)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'email'}  # This replaces ACCOUNT_AUTHENTICATION_METHOD
# Keep this so username isn't asked
ACCOUNT_EMAIL_VERIFICATION = 'none' # Change to 'mandatory' later if you want email confirmation
SOCIALACCOUNT_LOGIN_ON_GET = True   # Skips the intermediate "Continue as..." screen


# --- ADAPTERS (Connecting Google to your User Model) ---
# Since you deleted 'accounts', put the adapters.py file inside 'users' folder!
ACCOUNT_ADAPTER = 'users.adapters.MyAccountAdapter'


# --- SOCIAL PROVIDERS (Google & Facebook) ---
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_SECRET'),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'facebook': {
        'APP': {
            'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
            'secret': os.getenv('FACEBOOK_SECRET'),
            'key': ''
        },
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name'],
        'EXCHANGE_TOKEN': True,
    }
}

# --- EMAIL BACKEND (For testing) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'






#* JAZZMIN SETTINGS - ENHANCED BEAUTIFUL ADMIN PANEL
JAZZMIN_SETTINGS = {
    # ========== BRANDING ==========
    # Site title
    "site_title": "NCLEX Admin Dashboard",
    
    # Title on the login screen
    "site_header": "🩺 NCLEX Management",
    
    # Title on the brand (showing in sidebar)
    "site_brand": "NCLEX XAV",
    
    # Logo to use for your site (you can add a custom logo later)
    # "site_logo": "admin/img/nclex-logo.png",
    
    # Logo for the login screen
    "login_logo": None,
    
    # Small text under logo
    "site_logo_classes": "img-circle",
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to NCLEX Admin Panel",
    
    # Copyright on the footer
    "copyright": "NCLEX XAV Technology © 2025",
    
    # Search model in navbar (makes search more prominent)
    "search_model": ["users.Users", "questions.Questions"],
    
    # User avatar field
    "user_avatar": None,
    
    
    # ========== TOP MENU (Quick Actions) ==========
    "topmenu_links": [
        # Dashboard home
        {"name": "Dashboard", "url": "admin:index", "icon": "fas fa-tachometer-alt"},
        
        # Quick link to view website
        {"name": "View Website", "url": "/", "icon": "fas fa-home", "new_window": True},
        
        # Quick link to add new exam
        {"model": "exam_sessions.ExamSessions", "icon": "fas fa-plus-circle"},
        
        # Quick link to add new question
        {"model": "questions.Questions", "icon": "fas fa-plus-square"},
        
        # Support/Documentation link (you can customize this)
        {
            "name": "Documentation", 
            "url": "https://docs.djangoproject.com/", 
            "new_window": True,
            "icon": "fas fa-book"
        },
    ],
    
    
    # ========== USER MENU (Top Right) ==========
    "usermenu_links": [
        {"name": "View Profile", "url": "admin:users_users_change", "icon": "fas fa-user"},
        {"model": "users.Users"},
    ],
    
    
    # ========== SIDEBAR CONFIGURATION ==========
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Hide these apps (you can hide django's auth if using custom Users)
    "hide_apps": [],
    
    # Reorder models in sidebar (shows these first)
    "order_with_respect_to": [
        "users",
        "exam_sessions", 
        "questions",
        "scenarios",
        "categories",
        "user_responses",
    ],
    
    
    # ========== CUSTOM LINKS IN SIDEBAR ==========
    "custom_links": {
        "exam_sessions": [
            {
                "name": "Active Exams", 
                "url": "/admin/exam_sessions/examsessions/?status__exact=Ongoing",
                "icon": "fas fa-play-circle",
            },
            {
                "name": "Completed Exams",
                "url": "/admin/exam_sessions/examsessions/?status__exact=PASS",
                "icon": "fas fa-check-circle",
            },
        ],
        "questions": [
            {
                "name": "Add Bulk Questions",
                "url": "/admin/questions/questions/",
                "icon": "fas fa-plus-circle",
            },
        ],
    },
    
    
    # ========== BEAUTIFUL COLORFUL MEDICAL ICONS ==========
    "icons": {
        # 👥 User Management (Purple/Violet theme)
        "auth": "fas fa-shield-alt",  # Security shield
        "auth.Group": "fas fa-users",  # User groups
        "users.Users": "fas fa-user-nurse",  # Nurse icon
        "users.StudentProfile": "fas fa-id-card-clip",  # Student ID
        
        # 📋 Content Management (Blue theme)
        "questions.Questions": "fas fa-clipboard-question",  # Question clipboard
        "categories.Categories": "fas fa-folder-tree",  # Category folders
        "scenarios.Scenarios": "fas fa-book-medical",  # Medical case studies
        
        # 💻 Exam System (Green theme)
        "exam_sessions.ExamSessions": "fas fa-laptop-medical",  # Adaptive testing
        "user_responses.UserResponses": "fas fa-file-signature",  # Student responses
        
        # 🔗 Social Authentication (Orange theme)
        "socialaccount.SocialApp": "fas fa-share-nodes",  # OAuth apps
        "socialaccount.SocialAccount": "fas fa-user-check",  # Social accounts
        
        # ⚙️ System (Gray theme)
        "sites.Site": "fas fa-globe",  # Site configuration
    },
    
    # Default icons for parent/child items
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle-notch",
    
    
    # ========== RELATED MODAL (Makes editing smoother) ==========
    "related_modal_active": True,
    
    
    # ========== CUSTOM CSS/JS FOR MODERN DESIGN ==========
    "custom_css": "admin/css/custom_admin.css",  # Custom modern styling
    "custom_js": "admin/js/smooth_navigation.js",  # Smooth scroll & navigation
    
    
    # ========== LANGUAGE CHOOSER ==========
    "language_chooser": False,
}


# ========== JAZZMIN UI TWEAKS (MODERN WHITE THEME) ==========
JAZZMIN_UI_TWEAKS = {
    # ===== NAVBAR (Top Bar) =====
    "navbar_small_text": False,
    "navbar_fixed": True,  # Keep navbar visible on scroll
    "navbar": "navbar-white navbar-light",  # Clean white navbar
    "no_navbar_border": False,
    
    # ===== SIDEBAR (Left Menu) - MODERN WHITE! =====
    "sidebar_fixed": True,  # Keep sidebar visible on scroll
    "sidebar": "sidebar-light-primary",  # ✨ WHITE SIDEBAR with blue accents
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,  # Indent subsections
    "sidebar_nav_compact_style": False,  # More spacious
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,  # Modern look
    
    # ===== BRAND/LOGO =====
    "brand_small_text": False,
    "brand_colour": "navbar-primary",  # Blue brand color
    
    # ===== ACCENT COLOR =====
    "accent": "accent-primary",  # Blue accent for links/active items
    
    # ===== OVERALL LAYOUT =====
    "layout_boxed": False,  # Full-width layout
    "footer_small_text": False,
    "footer_fixed": False,
    "body_small_text": False,
    
    # ===== THEME =====
    "theme": "flatly",  # Clean, modern, flat theme (blue-based)
    "dark_mode_theme": None,  # No dark mode
    
    # ===== BUTTON STYLES =====
    "button_classes": {
        "primary": "btn-primary",      # Blue
        "secondary": "btn-secondary",  # Gray
        "info": "btn-info",            # Light blue
        "warning": "btn-warning",      # Yellow
        "danger": "btn-danger",        # Red
        "success": "btn-success"       # Green
    },
    
    # ===== ACTIONS (Bulk Actions) =====
    "actions_sticky_top": True,  # Keep action buttons visible
}

