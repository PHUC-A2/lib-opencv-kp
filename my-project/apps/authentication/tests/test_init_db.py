import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class InitDbCommandTests(TestCase):
    def test_init_db_creates_admin_from_env(self):
        env = {
            "ADMIN_USERNAME": "env_admin",
            "ADMIN_EMAIL": "env_admin@test.com",
            "ADMIN_PASSWORD": "EnvAdmin@1234",
            "ADMIN_FULL_NAME": "Admin Tu Env",
        }
        with patch.dict(os.environ, env, clear=False):
            call_command("init_db", skip_migrate=True, skip_algorithms=True)

        admin = User.objects.get(username="env_admin")
        self.assertEqual(admin.email, "env_admin@test.com")
        self.assertEqual(admin.full_name, "Admin Tu Env")
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("EnvAdmin@1234"))

    def test_init_db_updates_existing_admin(self):
        User.objects.create_user(
            username="old_admin",
            email="old_admin@test.com",
            password="OldAdmin@1234",
            role="user",
        )

        env = {
            "ADMIN_USERNAME": "old_admin",
            "ADMIN_EMAIL": "old_admin@test.com",
            "ADMIN_PASSWORD": "NewAdmin@5678",
            "ADMIN_FULL_NAME": "Admin Cap Nhat",
        }
        with patch.dict(os.environ, env, clear=False):
            call_command("init_db", skip_migrate=True, skip_algorithms=True)

        admin = User.objects.get(username="old_admin")
        self.assertEqual(admin.role, "admin")
        self.assertEqual(admin.full_name, "Admin Cap Nhat")
        self.assertTrue(admin.check_password("NewAdmin@5678"))

    def test_init_db_rejects_weak_password(self):
        env = {
            "ADMIN_USERNAME": "weak_admin",
            "ADMIN_EMAIL": "weak_admin@test.com",
            "ADMIN_PASSWORD": "123456",
            "ADMIN_FULL_NAME": "Weak Admin",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaises(Exception):
                call_command("init_db", skip_migrate=True, skip_algorithms=True)

        self.assertFalse(User.objects.filter(username="weak_admin").exists())
