
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app_werewolfkill.urls")),
]

if settings.DEBUG:
    # 僅開發環境下才自動提供媒體檔案服務
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)