#!/usr/bin/env python
import sys

if __name__ == "__main__":
    from settings import configure_settings
    configure_settings()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
