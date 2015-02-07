from .base import *

if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

TEST_DISCOVER_TOP_LEVEL = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))
