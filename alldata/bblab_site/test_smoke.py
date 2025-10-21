"""
Smoke tests to verify the Docker container build is working correctly.
"""


def test_imports():
    """Test that core dependencies can be imported."""
    import django
    import numpy
    import scipy
    import yaml
    assert django.VERSION is not None
    assert numpy.__version__ is not None


def test_django_setup():
    """Test that Django can be set up (even without database)."""
    import os
    import django
    
    # Set minimal Django settings for testing
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bblab_site.settings')
    
    # We expect this to fail without proper environment variables,
    # but it should fail gracefully, not with import errors
    try:
        django.setup()
    except KeyError:
        # Expected - missing environment variables like BBLAB_WEB_ADDRESS
        pass


def test_python_version():
    """Test that we're running the expected Python version."""
    import sys
    assert sys.version_info >= (3, 12)
    assert sys.version_info < (3, 13)
