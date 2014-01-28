"""
Django settings for project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '991-0)9oz^p0p63yyht8&*epj37$siu4##km-l^$f+-igb=1oa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.messages',
    #'django.contrib.staticfiles',
    'project.data',
    'django_extensions',
    'django_pdb',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {

        # Backend module
        # Required!
        'ENGINE': 'django_cassandra.db',

        # Name keyspace
        # Required!
        'NAME': 'django_keyspace',

        # User, optional
        # Default: None
        #'USER': '',

        # Password, optional
        # Default: None
        #'PASSWORD': '',

        # Native connection
        # Default: False
        #'NATIVE': True

        # Host, optional, dafault: 'localhost'
        #'HOST': 'localhost',

        # Port number to connect, optional,
        # Default: 9160 for thrift, 8000 for native
        #'PORT': 9160,

        # Compression Whether to use compression. For Thrift connections,
        # this can be None or the name of some supported compression
        # type (like "GZIP"). For native connections, this is treated
        # as a boolean, and if true, the connection will try to find
        # a type of compression supported by both sides.
        # Default: None
        #'COMPRESSION': '',

        # Consistency level to use for CQL3 queries (optional);
        # "ONE" is the default CL, other supported values are:
        # "ANY", "TWO", "THREE", "QUORUM", "LOCAL_QUORUM",
        # "EACH_QUORUM" and "ALL"; overridable on per-query basis.
        # Default: 'ONE'
        #'CONSISTENCY_LEVEL: '',

        # Transport. If set, use this Thrift transport instead of creating one;
        # doesn't apply to native connections.
        # Default: None
        #'TRANSPORT': '',

        'TEST_NAME': 'django_keyspace_test',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

try:
    from .settings_local import *
except ImportError:
    pass

