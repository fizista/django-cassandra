
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
        'HOST': '10.0.3.3',

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
    },
#    'postgres': {
#        'NAME': 'django_keyspace',
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'USER': 'django_keyspace',
#        'PASSWORD': 'django_keyspace'
#    },
#    'mysql': {
#        'NAME': 'django_keyspace',
#        'ENGINE': 'django.db.backends.mysql',
#        'USER': 'django_keyspace',
#        'PASSWORD': 'django_keyspace'
#    }
}
