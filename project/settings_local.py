

DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra.db',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'DjangoTest',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '10.0.3.3',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '9160',  # Set to empty string for default. Not used with sqlite3.
        #'SUPPORTS_TRANSACTIONS': False,
        #'CASSANDRA_REPLICATION_FACTOR': 1,
        #'CASSANDRA_ENABLE_CASCADING_DELETES': True
    }
}