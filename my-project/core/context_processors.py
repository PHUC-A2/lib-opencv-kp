from core.navigation import build_menu


def navigation_menu(request):
    # Context processor cung cap menu sidebar cho template dashboard.
    if not request.user.is_authenticated:
        return {}

    return build_menu(request)
