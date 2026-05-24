from django.urls import reverse

from core.navigation import build_guest_menu, build_menu


def navigation_menu(request):
    # Context processor cung cap menu sidebar cho template dashboard.
    if request.user.is_authenticated:
        return {
            **build_menu(request),
            "is_guest_mode": False,
        }

    return {
        **build_guest_menu(),
        "is_guest_mode": True,
        "guest_login_url": reverse("authentication:login"),
        "guest_register_url": reverse("authentication:register"),
    }
