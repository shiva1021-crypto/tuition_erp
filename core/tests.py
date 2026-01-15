from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Institute, User

class FoundationModelTests(TestCase):
    def setUp(self):
        # Create a dummy institute for testing
        self.institute = Institute.objects.create(
            name="Alpha Tuition Center",
            code="ALPHA01",
            address="123 Tech Street"
        )

    def test_institute_creation(self):
        """Test if the Institute is created correctly."""
        self.assertEqual(self.institute.name, "Alpha Tuition Center")
        self.assertTrue(self.institute.is_active)

    def test_institute_code_uniqueness(self):
        """Test that two institutes cannot have the same code."""
        with self.assertRaises(IntegrityError):
            Institute.objects.create(
                name="CopyCat Center",
                code="ALPHA01" # Same code as setUp()
            )

    def test_user_assignment(self):
        """Test that a Teacher can be linked to an Institute."""
        teacher = User.objects.create_user(
            username="math_teacher",
            password="securepassword123",
            role=User.Roles.TEACHER,
            institute=self.institute,
            phone_number="9876543210"
        )
        self.assertEqual(teacher.institute, self.institute)
        self.assertEqual(teacher.role, "TEACHER")

    def test_super_admin_no_institute(self):
        """Test that a Super Admin can exist without an Institute."""
        admin = User.objects.create_user(
            username="boss_man",
            password="securepassword123",
            role=User.Roles.SUPER_ADMIN,
            institute=None  # Should be allowed
        )
        self.assertIsNone(admin.institute)