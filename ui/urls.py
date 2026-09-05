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
    # Statik unter einer Adresse, die die Fassung TRAEGT
    # (`/statik/v-<zahl>/viewer/...`). Der Grund steht in
    # `djangobase/fassungsstatik.py`: ES-Module erben eine Fassung aus der
    # ABFRAGE nicht an ihre relativen Importe, aus dem PFAD schon. Ohne das
    # stand am 05.09.2026 eine frische Einstiegsdatei neben Modulen von
    # gestern — einmal als leere Seite, einmal als stumm fehlende Funktion.
    path('', include('djangobase.fassungsstatik')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
