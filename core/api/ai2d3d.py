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

from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dseitendaten import Ai2d3dseitendaten
from ..dienste.ai2d3dtabellen import Ai2d3dtabellen
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
            return redirect('ai2d3d_test', kennung=job)
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
        return Ai2d3dendpunkte._jobseite(request, gefunden, test=True)

    @staticmethod
    def _jobseite(request, job, test):
        daten = Ai2d3dseitendaten.fuer(job)
        return render(request, 'ai2d3d.html', {'job': job, 'daten': daten, 'netze': daten['netze'], 'ist_test': test,
                                               'texturweg': Mesh3daitexturwahl.gewaehlt(), 'texturkante': Mesh3daitexturwahl.KANTE})
