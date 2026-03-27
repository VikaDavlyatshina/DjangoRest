import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management import call_command


def load_all_fixtures():
    fixtures = [
        "users/fixtures/groups.json",
        "users/fixtures/users.json",
        "lms/fixtures/courses.json",
        "lms/fixtures/lessons.json",
        "users/fixtures/payments.json",
        "users/fixtures/subscriptions.json"

    ]

    for fixture in fixtures:
        print(f"Загрузка {fixture}...")
        try:
            call_command("loaddata", fixture)
            print(f"✅ {fixture} загружен")
        except Exception as e:
            print(f"❌ Ошибка загрузки {fixture}: {e}")


if __name__ == "__main__":
    load_all_fixtures()
