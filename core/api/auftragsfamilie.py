# -*- coding: utf-8 -*-
"""Auftragsfamilie — Rümpfe, die die Auftragsseiten gemeinsam haben: Bildmodell, Mesh to 3D, Mesh-Figur, Blender-Modell, 2D3D Kleider (08.11.2026, Edgar: „mach nicht doppelten Code“).

Bis dahin trug jede Seite eine Kopie, die sich nur in den Klassen ihrer Familie unterschied (gefunden mit `ProjektTemp/_wegwerf/duplikate/funktionsduplikate.py`, verglichen mit
`core_vergleich.py`). Jede Seite behält ihre Ansicht — Dekoratoren, Adresse, Docstring — und ruft hier mit IHREN Klassen auf: Modell, Ablage, Arbeiter, Zustand, Speichern, Optionen,
Löschung, Vorlage. Die Reihenfolge der Schritte (erst der Auftrag, dann der Rumpf der Anfrage) ist die der Kopien.

    return Auftragsfamilie.datei(Meshauftrag, Meshablage, request, job_id, ordner, name)
"""
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshoptionen import Meshoptionen

__all__ = ['Auftragsfamilie']


class Auftragsfamilie:

    @staticmethod
    def zustand_rechnen(auftrag, arbeiter, zustand, job_id):
        """Zustand des Auftrags für die Seite; rechnet ihn kein Arbeitsprozess mehr, gilt er als gescheitert. `zustand`: Auftrag → dict."""
        job = get_object_or_404(auftrag, pk=job_id)
        if job.laeuft and not arbeiter.lebt(job):
            job.refresh_from_db()
            if job.laeuft:
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess lebt nicht mehr (auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        return zustand(job)

    @staticmethod
    def datei(auftrag, ablage, request, job_id, ordner, name):
        """Eine Datei aus der Ablage des Auftrags (`Auftragsdatei`: ETag, `?v=`, `?laden=1`)."""
        job = get_object_or_404(auftrag, pk=job_id)
        try:
            pfad = ablage(job.kennung).datei(ordner, name)
        except ValueError:
            raise Http404('Pfad') from None
        if not pfad.is_file():
            raise Http404('Datei %s' % name)
        return Auftragsdatei.antwort(request, pfad, herunterladen=request.GET.get('laden') == '1', kennung=request.GET.get('v'))

    @staticmethod
    def mehrere_loeschen(auftrag, rumpf, entfernen, request):
        """Aufträge mit den `ids` aus dem Rumpf entfernen (`entfernen`: die Methode der Seite)."""
        ids = rumpf(request).get('ids') or []
        n = 0
        for job in auftrag.objects.filter(pk__in=ids):
            entfernen(job)
            n += 1
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    def modell(auftrag, speichern, rumpf, request, job_id):
        """{name} → die Figur als Genesis-Modell (`speichern.fuer(job).modell_speichern`)."""
        job = get_object_or_404(auftrag, pk=job_id)
        if job.laeuft or not job.stellung():
            return JsonResponse({'error': 'Erst wenn die Figur fertig ist'}, status=409)
        try:
            name = speichern.fuer(job).modell_speichern(rumpf(request).get('name'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'modell': name})

    @staticmethod
    def iterationen_loeschen(auftrag, rumpf, loeschung, request, job_id):
        """Runden löschen — während eines Laufs nur vormerken (`loeschung`: Klasse der Seite)."""
        job = get_object_or_404(auftrag, id=job_id)
        try:
            runden = sorted({int(n) for n in rumpf(request).get('runden') or []})
        except (TypeError, ValueError):
            return JsonResponse({'error': '„runden“: eine Liste von Rundennummern'}, status=400)
        if not runden:
            return JsonResponse({'error': 'Keine Runde gewählt'}, status=400)
        weg = loeschung(job)
        weg.vormerken(runden)
        if job.laeuft:
            return JsonResponse({'ok': True, 'geloescht': [], 'vorgemerkt': weg.vorgemerkt()})
        geloescht = weg.abarbeiten()
        job.save(update_fields=['ergebnis', 'updated_at'])
        return JsonResponse({'ok': True, 'geloescht': geloescht, 'vorgemerkt': []})

    @staticmethod
    def einstellungen_speichern(auftrag, arbeiter, rumpf, optionen, request, job_id):
        """Optionen des Auftrags mischen und speichern — nicht, solange sein Arbeitsprozess lebt."""
        job = get_object_or_404(auftrag, pk=job_id)
        if job.laeuft and arbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag läuft — Änderungen erst nach dem Lauf'}, status=409)
        neu = rumpf(request).get('optionen')
        if isinstance(neu, dict):
            job.optionen = optionen.mischen(job.optionen, neu)
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'optionen': optionen.pruefen(job.optionen)})

    @staticmethod
    def foto_reihenfolge(job, rumpf, erneuern, antwort):
        """Ein Foto an eine andere Stelle schieben (`index` 1-basiert); wechselt Platz 1, wird die Vorlage erneuert (`erneuern`). Nicht über `bilder_sichern` (Docstring der Seite)."""
        datei = str(rumpf.get('datei') or '')
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            ziel = int(rumpf.get('index'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'index fehlt oder ist keine Zahl'}, status=400)
        ziel = max(0, min(len(bilder) - 1, ziel - 1))
        vorher = bilder[0].get('datei')
        bilder.insert(ziel, bilder.pop(stelle))
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        if bilder[0].get('datei') != vorher:
            erneuern(job)
        return antwort(job)

    @staticmethod
    def foto_gewicht(job, eintrag, rumpf):
        """Fotogewicht (0..100) und optionaler Bereich eines Bildeintrags speichern."""
        eintrag['gewicht'] = Meshoptionen.gewicht_pruefen(rumpf.get('gewicht'))
        if 'bereich' in rumpf:
            eintrag['bereich'] = Meshoptionen.bereich_pruefen(rumpf.get('bereich'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})
