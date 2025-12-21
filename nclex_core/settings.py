from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-3^0&6)j-dclz4(nfu&3j8(hrin#*t1gprc$v(@+x2stu2h%q76'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

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
    
    # ALLAUTH (Social Login)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',   # Google
    'allauth.socialaccount.providers.facebook', # Facebook
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
        'DIRS': [BASE_DIR / 'templates'],
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

# You only need this list if you have a "global" static folder outside the users app.
# Since your CSS is inside 'users/static', you can leave this empty or commented out.
STATICFILES_DIRS = [
    # BASE_DIR / 'static', 
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
ACCOUNT_LOGIN_METHODS = {'email'}  # This replaces ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_EMAIL_REQUIRED = True      # Keep this to ensure email is mandatory
ACCOUNT_USERNAME_REQUIRED = False
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



#* JAZZMIN SETTINGS
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "NCLEX Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "NCLEX Core",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "NCLEX Admin",

    # Logo to use for your site, must be present in static files, used for brand on top left
    # "site_logo": "books/img/logo.png",  # Upload a logo to your static folder later

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the NCLEX HQ",

    # Copyright on the footer
    "copyright": "NCLEX XAV Technology",

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/"},
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["users", "questions", "scenarios", "exam_sessions"],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.5.0,5.6.0
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "users.Users": "fas fa-user",
        "questions.Questions": "fas fa-question-circle",
        "scenarios.Scenarios": "fas fa-book-medical",
        "categories.Categories": "fas fa-tags",
        "exam_sessions.ExamSessions": "fas fa-stopwatch",
        "user_responses.UserResponses": "fas fa-pencil-alt",
    },
    
    # Icons that are used when one is not specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

# JAZZMIN UI TWEAKS (The Blue/White Modern Look)
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-white",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",  
    "sidebar_nav_small_text": False,
    "theme": "flatly",  # A clean, modern, flat theme
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}