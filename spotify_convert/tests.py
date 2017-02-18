from django.test import TestCase
from .models import UserProfile

# Create your tests here.

def test_refresh():
    from .helper import refresh_token
    profile = UserProfile.objects.get(email="mvasiliou94@gmail.com")
    refresh_token(profile)


def test_library():
    from .tasks import go
    profile = UserProfile.objects.get(email="mvasiliou94@gmail.com")
    go('library.xml',profile)