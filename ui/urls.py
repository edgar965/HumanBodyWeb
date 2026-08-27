from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Logs / Versionen / Tests / Einstellungen / Werkzeuge — aus djangoBase.
    #
    # `hilfe/` UND NICHT `help/` (28.08.2026): djangoBase schreibt deutsche
    # Hilfe-Adressen vor (`djangobase.tests.konform.test_hilfe_seiten`), und
    # alle sechs Projekte hängen dort. Der englische Präfix hat in 3DTools
    # bis zum 27.08.2026 stillschweigend Schaden angerichtet: Vier
    # mitgelieferte JS-Module riefen fest `/hilfe/tests/aufzeichnung/` und
    # liefen bei JEDEM Seitenaufruf dreimal in eine 404 — ohne Fehlerseite,
    # ohne Eintrag im Fehlerlog.
    path('hilfe/', include('djangobase.urls')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
