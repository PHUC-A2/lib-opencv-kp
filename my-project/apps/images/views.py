from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.images.forms import GalleryFilterForm, ImageUploadForm
from apps.images.models import Image
from apps.images.services.image_service import ImageService, ImageUploadError


@login_required
def upload_view(request: HttpRequest) -> HttpResponse:
    # Trang upload anh drag & drop.
    form = ImageUploadForm()

    return render(
        request,
        "images/upload.html",
        {
            "page_title": "Tải ảnh lên",
            "page_subtitle": "Kéo thả hoặc chọn ảnh để upload",
            "form": form,
        },
    )


@login_required
@csrf_protect
@require_POST
def upload_process_view(request: HttpRequest) -> HttpResponse:
    # Xu ly upload anh qua HTMX (ho tro nhieu file).
    uploaded_files = request.FILES.getlist("file")
    if not uploaded_files:
        uploaded_files = request.FILES.getlist("files")

    if not uploaded_files:
        return render(
            request,
            "images/partials/upload_status.html",
            {
                "status": "error",
                "message": "Vui lòng chọn ít nhất một ảnh.",
            },
            status=400,
        )

    uploaded_images = []
    errors = []

    for uploaded_file in uploaded_files:
        try:
            image = ImageService.upload_image(request.user, uploaded_file)
            uploaded_images.append(image)
        except ImageUploadError as exc:
            errors.append(f"{uploaded_file.name}: {exc}")

    if not uploaded_images and errors:
        return render(
            request,
            "images/partials/upload_status.html",
            {
                "status": "error",
                "message": errors[0],
                "errors": errors,
            },
            status=400,
        )

    return render(
        request,
        "images/partials/upload_result.html",
        {
            "uploaded_images": uploaded_images,
            "errors": errors,
            "status": "done" if uploaded_images else "error",
        },
    )


@login_required
def gallery_view(request: HttpRequest) -> HttpResponse:
    # Trang thu vien anh cua user.
    filter_form = GalleryFilterForm(request.GET or None)
    search = ""
    sort = "newest"

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search", "")
        sort = filter_form.cleaned_data.get("sort") or "newest"

    images = ImageService.get_user_images(request.user, search=search, sort=sort)

    context = {
        "page_title": "Thư viện ảnh",
        "page_subtitle": f"{images.count()} ảnh trong thư viện",
        "filter_form": filter_form,
        "images": images,
        "search": search,
        "sort": sort,
    }

    if request.headers.get("HX-Request"):
        return render(request, "images/partials/gallery_grid.html", context)

    return render(request, "images/gallery.html", context)


@login_required
@csrf_protect
@require_POST
def delete_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Xoa anh khoi thu vien (HTMX).
    try:
        ImageService.delete_image(request.user, pk)
    except Image.DoesNotExist:
        if request.headers.get("HX-Request"):
            return render(
                request,
                "images/partials/upload_status.html",
                {
                    "status": "error",
                    "message": "Không thể xóa ảnh. Vui lòng thử lại.",
                },
                status=404,
            )
        messages.error(request, "Không thể xóa ảnh. Vui lòng thử lại.")
        return redirect("images:gallery")

    if request.headers.get("HX-Request"):
        return HttpResponse("")

    messages.success(request, "Đã xóa ảnh thành công.")
    return redirect("images:gallery")


@login_required
def download_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Tai anh ve may client.
    try:
        image = ImageService.get_user_image(request.user, pk)
        file_path = ImageService.get_absolute_file_path(image)
    except Image.DoesNotExist as exc:
        raise Http404("Không tìm thấy ảnh.") from exc

    response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=image.original_filename)
    response["Content-Type"] = image.mime_type
    return response
