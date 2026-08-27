# -*- coding: utf-8 -*-
"""Seiten des Web-Teils — Vorlagen, keine Fachlogik.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.

UMBAU 27.08.2026 (Befund `freie-funktionen`): zehn freie Funktionen, keine
Klasse. Sie stehen jetzt als Methoden in `Webseiten` — und die beiden, die
denselben Auftrag aufloesen (`auftragsseite`, `ergebnisseite`), holen ihn ueber
eine gemeinsame Hilfsmethode statt jede fuer sich.
"""

import os

from django.shortcuts import render, redirect, get_object_or_404

from ..dienste.systemzustand import Systemzustand
from ..models import BVHJob


class Webseiten:
    """Die Seiten des Video-zu-BVH-Teils. Jede rendert nur eine Vorlage."""

    @staticmethod
    def start(request):
        """`/` zeigt die Ergebnisseite."""
        return redirect('standalone_result')

    @staticmethod
    def werkzeugstatus(request):
        """MocapNET-Systemzustand und die letzten Auftraege.

        Review 16.08.2026: `bvh_count` ist entfallen. Die Zahl wurde bei jedem
        Aufruf per COUNT(*) geholt und der Vorlage uebergeben, die sie nirgends
        anzeigt.
        """
        return render(request, 'test_mocapnet.html', {
            'status': Systemzustand.holen(),
            'recent_jobs': BVHJob.objects.all()[:10],
        })

    # --------------------------------------------------------- Ein Auftrag

    @staticmethod
    def _auftrag(job_id):
        return get_object_or_404(BVHJob, id=job_id)

    @classmethod
    def auftragsseite(cls, request, job_id):
        """Der Fortschritt eines laufenden Auftrags."""
        return render(request, 'job_status.html',
                      {'job': cls._auftrag(job_id)})

    @classmethod
    def ergebnisseite(cls, request, job_id):
        """Ergebnis-Ansicht mit Video und BVH-Skelett."""
        return render(request, 'job_result.html',
                      {'job': cls._auftrag(job_id)})

    # -------------------------------------------------------------- Listen

    @staticmethod
    def ergebnisauswahl(request):
        """Ergebnisseite mit Auswahlliste statt festem Auftrag."""
        fertige = BVHJob.objects.filter(status='complete').order_by('-created_at')
        auftrag = None
        gewaehlt = request.GET.get('job')
        if gewaehlt:
            auftrag = get_object_or_404(BVHJob, id=gewaehlt, status='complete')
        elif fertige.exists():
            auftrag = fertige.first()
        return render(request, 'standalone_result.html',
                      {'job': auftrag, 'jobs': fertige})

    @staticmethod
    def fertigliste(request):
        """Alle fertigen Auftraege mit Vorschaubild."""
        auftraege = BVHJob.objects.filter(status='complete')
        # `bvh_basename` haengt nur fuer die Vorlage am Objekt.
        for auftrag in auftraege:
            auftrag.bvh_basename = (os.path.basename(auftrag.bvh_file)
                                    if auftrag.bvh_file else '—')
        return render(request, 'processed.html', {'jobs': auftraege})

    @staticmethod
    def bvhbibliothek(request):
        """BVH-Dateien durchsuchen — seitenweise, siehe Bvhbibliothek."""
        from ..dienste.bvhbibliothek import Bvhbibliothek
        return render(request, 'browser.html',
                      Bvhbibliothek.aus_anfrage(request).zusammenhang())

    @staticmethod
    def webcam(request):
        """Aufnahme ueber die angeschlossene Kamera."""
        return render(request, 'webcam.html')

    # ------------------------------------------------------ Weiterleitungen

    @staticmethod
    def einstellungen(request):
        """`/settings/` zeigt auf `/settings/model/`."""
        return redirect('settings_model')

    @staticmethod
    def einstellungen_videobvh(request):
        """Alte Adresse — jetzt die 2D-Einstellungen."""
        return redirect('settings_videobvh_2d')
