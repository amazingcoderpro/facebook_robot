
import requests
from django.test import TestCase

# Create your tests here.


# class AuthTestCase(TestCase):
#
#     def test_auth(self):
#         r = requests.post('http://127.0.0.1:8000/api/user/auth', json={"username": "user1", "password": "user1"})
#         self.assertEqual(r.status_code, 200)


r = requests.post('http://127.0.0.1:8000/api/user/auth', json={"username": "user1", "password": "user1"})
print(r.status_code)
print(r.text)

