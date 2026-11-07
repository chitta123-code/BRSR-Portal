from django.urls import path
from .views import (
    upload_esg_file,
    preview_esg_file,
    import_esg_file,
)

urlpatterns = [
    path(
        "",
        upload_esg_file,
        name="ingestion_home"
    ),

    path(
        "upload/",
        upload_esg_file,
        name="upload_esg_file"
    ),

    path(
        "preview/<int:file_id>/",
        preview_esg_file,
        name="preview_esg_file"
    ),

    path(
        "import/<int:file_id>/",
        import_esg_file,
        name="import_esg_file"
    ),
]