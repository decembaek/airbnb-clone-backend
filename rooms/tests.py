# from django.test import TestCase -> 이거 대신 Rest framework 사용
from rest_framework.test import APITestCase


# Create your tests here.
# TEST 방법
class TestAmenities(APITestCase):
    def test_two_plus_two(self):
        self.assertEqual(2 + 2, 4, "The math is wrong.")
