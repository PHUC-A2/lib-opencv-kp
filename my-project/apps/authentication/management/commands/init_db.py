from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.authentication.services.init_db_service import InitDbService, InitDbServiceError


class Command(BaseCommand):
    help = "Khoi tao database: migrate, tao/cap nhat admin tu .env, seed thuat toan mac dinh"

    def add_arguments(self, parser):
        # Cho phep bo qua migrate hoac seed khi can.
        parser.add_argument(
            "--skip-migrate",
            action="store_true",
            help="Bo qua buoc chay migrate",
        )
        parser.add_argument(
            "--skip-algorithms",
            action="store_true",
            help="Bo qua buoc seed thuat toan mac dinh",
        )

    def handle(self, *args, **options):
        # Luong khoi tao database end-to-end.
        if not options["skip_migrate"]:
            self.stdout.write("Dang chay migrate...")
            call_command("migrate", interactive=False, verbosity=0)
            self.stdout.write(self.style.SUCCESS("Migrate xong."))

        try:
            config = InitDbService.get_admin_config()
            admin_user, created = InitDbService.upsert_admin_user(config)
        except InitDbServiceError as exc:
            raise CommandError(str(exc)) from exc

        action_label = "Tao moi" if created else "Cap nhat"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action_label} tai khoan admin: {admin_user.username} ({admin_user.email})"
            )
        )

        if not options["skip_algorithms"]:
            self.stdout.write("Dang seed thuat toan mac dinh...")
            call_command("seed_algorithms", verbosity=0)

        self.stdout.write(self.style.SUCCESS("Khoi tao database hoan tat."))
