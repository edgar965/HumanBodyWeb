# -*- coding: utf-8 -*-
"""Ai2d3dendpunkte — die Seiten von „2d-3d-AI“ (24.10.2026, Dashboard → 2d-3d-AI).

Edgar: „mach eine Kopie von Dashboard - Mesh3d-AI ohne Inhalte (nur Seiten …) und benenne sie 2d-3d-AI“, danach „passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell
und das Ergebnis zu sehen ist, mit den ganzen Views und Filter (z.B. Textur, Kleider) so wie bei den Mesh3d-AI Jobs“.

GET /2d-3d-AI/                      die Liste wie /mesh-3D-AI/: Jobs (Exporte mit Wahrheit) · Test (echte Fotos) · Formtraining · Lauf Aktuell (`Ai2d3dtabellen`)
GET /2d-3d-AI/<job>/                die Jobseite: Fotos · Netz · Genesis-Modell · Ergebnis und der Vergleich aus allen Perspektiven; unbekannter Job → 404, andere Schreibweise → Umleitung
GET /2d-3d-AI/test/<kennung>/       dieselbe Seite für einen Test (echte Fotos, ohne Wahrheit)

Fotos und Netze liefert `Ai2d3ddatenendpunkte`; die Genesis-Figur holt der Browser bei Mesh3D-AI (`Ai2d3dseitendaten`).
"""

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from ..dienste.ai2d3dform import Ai2d3dform
from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dnormalen import Ai2d3dnormalen
from ..dienste.ai2d3dgeschlecht import Ai2d3dgeschlecht
from ..dienste.ai2d3dpshuman import Ai2d3dpshuman
from ..dienste.ai2d3dpshumaneingabe import Ai2d3dpshumaneingabe
from ..dienste.ai2d3dseitendaten import Ai2d3dseitendaten
from ..dienste.ai2d3dtabellen import Ai2d3dtabellen
from ..dienste.ai2d3dtextur import Ai2d3dtextur
from ..dienste.mesh3daitexturwahl import Mesh3daitexturwahl

__all__ = ['Ai2d3dendpunkte']


class Ai2d3dendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        return render(request, 'ai2d3d_liste.html', Ai2d3dtabellen.alle())

    @staticmethod
    @require_GET
    def seite(request, job):
        """Ein Export (Reiter „Jobs“). Ein Test unter dieser Adresse leitet auf seine Testadresse um."""
        if job != job.lower():
            return redirect('ai2d3d_job', job=job.lower())
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        if gefunden['art'] != 'export':
            return redirect('ai2d3d_test', kennung=gefunden['adresse'])
        return Ai2d3dendpunkte._jobseite(request, gefunden, test=False)

    @staticmethod
    @require_GET
    def test(request, kennung):
        """Echte Fotos (Reiter „Test“): dieselbe Seite wie ein Job, ohne Wahrheit."""
        if kennung != kennung.lower():
            return redirect('ai2d3d_test', kennung=kennung.lower())
        gefunden = Ai2d3djobs.job(kennung)
        if gefunden is None:
            raise Http404('Kein Test %s' % kennung)
        if gefunden['art'] == 'export':
            return redirect('ai2d3d_job', job=kennung)
        if kennung != gefunden['adresse']:                                 # die alte Adresse eines umbenannten Tests (`Ai2d3dadresse`)
            return redirect('ai2d3d_test', kennung=gefunden['adresse'])
        return Ai2d3dendpunkte._jobseite(request, gefunden, test=True)

    @staticmethod
    def _jobseite(request, job, test):
        daten = Ai2d3dseitendaten.fuer(job)
        return render(request, 'ai2d3d.html', {'job': job, 'daten': daten, 'netze': daten['netze'], 'ist_test': test,
                                               'texturweg': Mesh3daitexturwahl.gewaehlt(), 'texturkante': Mesh3daitexturwahl.KANTE,
                                               'normalen_engines': Ai2d3dendpunkte._engines(),
                                               'normalen_zusammen': Ai2d3dnormalen.ZUSAMMEN,
                                               'textur_engines': Ai2d3dtextur.auswahl(),
                                               'form_engines': Ai2d3dform.auswahl(),
                                               'pshuman_wege': Ai2d3dpshuman.auswahl(),
                                               'pshuman_anzahlen': Ai2d3dpshuman.ANZAHL,
                                               'pshuman_dichten': Ai2d3dpshuman.DICHTEN,
                                               'geschlechter': Ai2d3dgeschlecht.WAHL,
                                               'pshuman_vorschlag': Ai2d3dpshumaneingabe.VORSCHLAG})

    @staticmethod
    def _engines():
        """Combo-Box „Normalen“ (03.11.2026): Wert, Text, Beschreibung je Engine."""
        b = Ai2d3dnormalen.BESCHREIBUNG
        return [{'wert': w, 'text': t, 'beschreibung': b[w]} for w, t in Ai2d3dnormalen.ENGINES]
