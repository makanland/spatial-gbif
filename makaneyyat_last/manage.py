#!/usr/bin/env python
import os
import sys
from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Makaneyyat.settings.dev")
    if 'gsecretkey' in sys.argv:
        print('Copy the secret key to your setting file.')
        print(get_random_secret_key())
        exit();
    # get_random_secret_key()
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
