from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def role_required(*roles: str):
    # Decorator kiem tra quyen truy cap theo role user.
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user_role = getattr(request.user, "role", "user")
            if user_role not in roles:
                messages.error(request, "Bạn không có quyền truy cập trang này.")
                return redirect("dashboard:home")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required("admin")
