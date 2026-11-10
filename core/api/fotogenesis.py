# -*- coding: utf-8 -*-
"""Fotogenesisendpunkte — die Seiten von „Foto-Genesis“ (24.10.2026, Dashboard → Foto-Genesis).

Edgar: „mach eine Kopie von Dashboard - Mesh3d-AI ohne Inhalte (nur Seiten …) und benenne sie 2d-3d-AI“, danach „passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell
und das Ergebnis zu sehen ist, mit den ganzen Views und Filter (z.B. Textur, Kleider) so wie bei den Mesh3d-AI Jobs“.

GET /foto-genesis/                      die Liste wie /mesh-genesis/: Jobs (Exporte mit Wahrheit) · Test (echte Fotos) · Formtraining · Lauf Aktuell (`Fotogenesistabellen`)
GET /foto-genesis/<job>/                die Jobseite: Fotos · Netz · Genesis-Modell · Ergebnis und der Vergleich aus allen Perspektiven; unbekannter Job → 404, andere Schreibweise → Umleitung
GET /foto-genesis/test/<kennung>/       dieselbe Seite für einen Test (echte Fotos, ohne Wahrheit)

Fotos und Netze liefert `Fotogenesisdatenendpunkte`; die Genesis-Figur holt der Browser bei Mesh-Genesis (`Fotogenesisseitendaten`).
"""

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from ..dienste.fotogenesisform import Fotogenesisform
from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.fotogenesisnormalen import Fotogenesisnormalen
from ..dienste.fotogenesisgeschlecht import Fotogenesisgeschlecht
from ..dienste.fotogenesispshuman import Fotogenesispshuman
from ..dienste.fotogenesispshumaneingabe import Fotogenesispshumaneingabe
from ..dienste.fotogenesisseitendaten import Fotogenesisseitendaten
from ..dienste.fotogenesistabellen import Fotogenesistabellen
from ..dienste.fotogenesistextur import Fotogenesistextur
from ..dienste.meshgenesistexturwahl import Meshgenesistexturwahl

__all__ = ['Fotogenesisendpunkte']


class Fotogenesisendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        return render(request, 'fotogenesis_liste.html', Fotogenesistabellen.alle())

    @staticmethod
    @require_GET
    def seite(request, job):
        """Ein Export (Reiter „Jobs“). Ein Test unter dieser Adresse leitet auf seine Testadresse um."""
        if job != job.lower():
            return redirect('fotogenesis_job', job=job.lower())
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        if gefunden['art'] != 'export':
            return redirect('fotogenesis_test', kennung=gefunden['adresse'])
        return Fotogenesisendpunkte._jobseite(request, gefunden, test=False)

    @staticmethod
    @require_GET
    def test(request, kennung):
        """Echte Fotos (Reiter „Test“): dieselbe Seite wie ein Job, ohne Wahrheit."""
        if kennung != kennung.lower():
            return redirect('fotogenesis_test', kennung=kennung.lower())
        gefunden = Fotogenesisjobs.job(kennung)
        if gefunden is None:
            raise Http404('Kein Test %s' % kennung)
        if gefunden['art'] == 'export':
            return redirect('fotogenesis_job', job=kennung)
        if kennung != gefunden['adresse']:                                 # die alte Adresse eines umbenannten Tests (`Fotogenesisadresse`)
            return redirect('fotogenesis_test', kennung=gefunden['adresse'])
        return Fotogenesisendpunkte._jobseite(request, gefunden, test=True)

    @staticmethod
    def _jobseite(request, job, test):
        daten = Fotogenesisseitendaten.fuer(job)
        return render(request, 'fotogenesis.html', {'job': job, 'daten': daten, 'netze': daten['netze'], 'ist_test': test,
                                               'texturweg': Meshgenesistexturwahl.gewaehlt(), 'texturkante': Meshgenesistexturwahl.KANTE,
                                               'normalen_engines': Fotogenesisendpunkte._engines(),
                                               'normalen_zusammen': Fotogenesisnormalen.ZUSAMMEN,
                                               'textur_engines': Fotogenesistextur.auswahl(),
                                               'form_engines': Fotogenesisform.auswahl(),
                                               'pshuman_wege': Fotogenesispshuman.auswahl(),
                                               'pshuman_anzahlen': Fotogenesispshuman.ANZAHL,
                                               'pshuman_dichten': Fotogenesispshuman.DICHTEN,
                                               'geschlechter': Fotogenesisgeschlecht.WAHL,
                                               'pshuman_vorschlag': Fotogenesispshumaneingabe.VORSCHLAG})

    @staticmethod
    def _engines():
        """Combo-Box „Normalen“ (03.11.2026): Wert, Text, Beschreibung je Engine."""
        b = Fotogenesisnormalen.BESCHREIBUNG
        return [{'wert': w, 'text': t, 'beschreibung': b[w]} for w, t in Fotogenesisnormalen.ENGINES]
