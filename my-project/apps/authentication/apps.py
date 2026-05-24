from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    # Khai bao kieu primary key mac dinh cho model.
    default_auto_field = "django.db.models.BigAutoField"
    # Ten day du cua app de Django nhan dien dung package.
    name = "apps.authentication"
    # Label dung cho AUTH_USER_MODEL.
    label = "authentication"
    # Ten hien thi trong admin.
    verbose_name = "Xac thuc nguoi dung"
