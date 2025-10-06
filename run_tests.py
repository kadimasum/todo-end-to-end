#!/usr/bin/env python
"""
Test runner script for TodoApp
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo_project.settings")
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["todo_app"])
    if failures:
        sys.exit(1)
