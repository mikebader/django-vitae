import os
import sys

BASE_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.dirname(BASE_DIR))

SECRET_KEY = 'fake-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'tests.test_urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'cv',
    'tests',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    # '--attr=book', ## use command-line arguments
    '--verbosity=1',
    '--with-doctest',
    # '--with-coverage',
    # '--cover-package=cv',
    # '--cover-inclusive',
    # '--cover-html',
    # '--cover-html-dir=tests/html'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'static', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cv.context_processors.cv_personal_info',
            ],
        },
    },
]

MEDIA_ROOT = '/Users/bader/tmp/'
MEDIA_URL = '/media/'


