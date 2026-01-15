# academics/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User, Institute

class StudentOnboardingTests(APITestCase):
    def setUp(self):
        # 1. Setup the Institute
        self.institute = Institute.objects.create(name="Test Academy", code="TEST01")
        
        # 2. Setup the Admin User (who will do the onboarding)
        self.admin_user = User.objects.create_user(
            username="admin_user", 
            password="password123", 
            role=User.Roles.INSTITUTE_ADMIN,
            institute=self.institute
        )
        
        # 3. Authenticate (This simulates logging in and getting the token)
        self.client.force_authenticate(user=self.admin_user)

    def test_create_student_success(self):
        """
        Ensure we can create a student with a profile in one go.
        """
        url = reverse('students-list') # Matches router.register('students', ...)
        data = {
            "username": "new_student",
            "password": "securePass123",
            "first_name": "Rahul",
            "last_name": "Dravid",
            "email": "rahul@example.com",
            "profile": {
                "date_of_birth": "2012-01-01",
                "parent_name": "Mr. Dravid",
                "parent_phone": "9876543210",
                "address": "Bangalore",
                "enrollment_number": "BATCH-2026-001"
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check 1: Did the API say "Created"?
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check 2: Was the user actually created in DB?
        self.assertTrue(User.objects.filter(username="new_student").exists())
        
        # Check 3: Is the profile linked?
        new_student = User.objects.get(username="new_student")
        self.assertEqual(new_student.student_profile.enrollment_number, "BATCH-2026-001")
        
        # Check 4: Is the Institute correctly assigned?
        self.assertEqual(new_student.institute, self.institute)

    def test_create_student_unauthorized(self):
        """
        Ensure someone without a token cannot create a student.
        """
        self.client.logout() # Remove authentication
        url = reverse('students-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)