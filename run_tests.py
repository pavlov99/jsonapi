import sys
import django
from django.conf import settings


def main():
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'jsonapi.tests.testapp',
            'jsonapi',
        ],
        # Django replaces this, but it still wants it. *shrugs*
        DATABASE_ENGINE='django.db.backends.sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        ROOT_URLCONF='jsonapi.tests.testapp.urls',
        DEBUG=True,
        TEMPLATE_DEBUG=True,
    )

    if django.VERSION[:2] >= (1, 7):
        django.setup()

    apps = ['jsonapi']
    #if django.VERSION[:2] >= (1, 6):
        #apps.append('jsonapi.tests.testapp')
        #apps.append('jsonapi.tests')

    from django.core.management import call_command
    from django.test.utils import get_runner

    try:
        from django.contrib.auth import get_user_model
    except ImportError:
        USERNAME_FIELD = "username"
    else:
        USERNAME_FIELD = get_user_model().USERNAME_FIELD

    DjangoTestRunner = get_runner(settings)

    class TestRunner(DjangoTestRunner):
        def setup_databases(self, *args, **kwargs):
            result = super(TestRunner, self).setup_databases(*args, **kwargs)
            kwargs = {
                "interactive": False,
                "email": "admin@doesnotexit.com",
                USERNAME_FIELD: "admin",
            }
            call_command("createsuperuser", **kwargs)
            return result

    failures = TestRunner(verbosity=2, interactive=True).run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    main()
