import os
import dj_database_url
import dotenv
import environ
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '##*)vr0=w5!0tllan#0&4nwd-3!anr68mz=m8nbpql3y&v#i8%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'aureum.apps.AureumConfig',
    'clear_cache',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'unchained.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'unchained.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {'default': dj_database_url.config(default='postgres://jsnmfiqtcggjyu:368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9@ec2-34-233-226-84.compute-1.amazonaws.com:5432/d77knu57t1q9j9')}
#DATABASES['default'] = dj_database_url.config(default='postgres://jsnmfiqtcggjyu:368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9@ec2-34-233-226-84.compute-1.amazonaws.com:5432/d77knu57t1q9j9')
#DATABASES = {'default': dj_database_url.config(default='postgres://user:pass@localhost/dbname')}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    #'/var/www/static/',
]

#django_heroku.settings(locals())
#DATABASES = {'default': dj_database_url.config('postgres://jsnmfiqtcggjyu:368e05099543272efb167e9fa3173338be43c1e787666ed2478f51ef050707b9@ec2-34-233-226-84.compute-1.amazonaws.com:5432/d77knu57t1q9j9')}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd7p3fuehaleleo',
        'USER': 'snbetggfklcniv',
        'PASSWORD': '7798f45239eda70f8278ce3c05dc632ad57b97957b601681a3c516f37153403a',
        'HOST': 'ec2-34-197-188-147.compute-1.amazonaws.com',
        'PORT': '5432'
    }
}

""" DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600) """

options = DATABASES['default'].get('OPTIONS', {})
options.pop('sslmode', None)