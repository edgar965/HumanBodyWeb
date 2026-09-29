# -*- coding: utf-8 -*-
"""Meshfotoendpunkte — Fotos eines Mesh-Auftrags austauschen (29.09.2026).

Edgar: „in … möchte ich die Fotos der Vorlage ersetzen können (Datei suche - auswahl dialog
und Ordner auswahl, dann werden mir alle Bilder gelistet) - bei Bereich „Fotos"". Bis dahin
standen die Fotos eines Auftrags fest, sobald er angelegt war; wer ein besseres Rückenfoto
hatte, musste einen neuen Auftrag anlegen.

    POST /api/mesh/<id>/fotos/                  (multipart: bilder)  → anhängen
    POST /api/mesh/<id>/foto/<datei>/ersetzen/  (multipart: bild)    → an Ort und Stelle
    POST /api/mesh/<id>/foto/<datei>/loeschen/                       → entfernen
    → {ok, bilder: [...]}

**Warum die vorbereitete Fassung mit weg muss:** `vorbereitet/<stamm>.png` ist das
freigestellte, lichtausgeglichene Foto aus einem früheren Lauf. Der Runner verwendet es
wieder, wenn es da ist — ein ersetztes Foto würde sonst still ignoriert und der nächste Lauf
rechnete mit dem alten Bild weiter. Genau diese Sorte Fehler sieht man erst im Ergebnis.

Ein laufender Auftrag wird nicht angefasst (409): Der Arbeitsprozess liest `eingang/`
und schreibt `bilder` zurück.
"""

import logging
import os

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.meshablage import Meshablage
from ..models import Meshauftrag

logger = logging.getLogger('core')

__all__ = ['Meshfotoendpunkte']


class Meshfotoendpunkte:

    @staticmethod
    def _job(job_id):
        return get_object_or_404(Meshauftrag, id=job_id)

    @staticmethod
    def _vorbereitetes_loeschen(ablage, datei):
        """Die freigestellte Fassung eines Fotos verwerfen — sonst rechnet der nächste Lauf
        mit dem alten Bild weiter."""
        stamm = os.path.splitext(str(datei))[0]
        ordner = ablage.unter(Meshablage.VORBEREITET)
        if not ordner.is_dir():
            return
        for pfad in ordner.glob(stamm + '.*'):
            try:
                pfad.unlink()
            except OSError:
                logger.warning('Vorbereitetes Foto %s ließ sich nicht löschen', pfad)

    @staticmethod
    def _antwort(job):
        return JsonResponse({'ok': True, 'bilder': job.bilder})

    # ------------------------------------------------------------- Endpunkte

    @staticmethod
    @require_POST
    def hinzufuegen(request, job_id):
        job = Meshfotoendpunkte._job(job_id)
        if job.laeuft:
            return JsonResponse({'error': 'Der Auftrag rechnet gerade — erst anhalten'}, status=409)
        dateien = [f for f in request.FILES.getlist('bilder') if Meshablage.ist_bild(f.name)]
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        ablage = Meshablage(job.kennung)
        bilder = list(job.bilder or [])
        for hochgeladen in dateien:
            gespeichert = ablage.eingang_ablegen(hochgeladen)
            bilder.append({'datei': gespeichert, 'original': hochgeladen.name,
                           'gewicht': 100, 'bereich': None, 'rolle': 'aus'})
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Mesh %s: %d Foto(s) hinzugefügt', job.kennung, len(dateien))
        return Meshfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def ersetzen(request, job_id, datei):
        """Ein Foto austauschen — Rolle, Gewicht, Bereich und Platz bleiben.

        Die neue Datei bekommt einen eigenen Namen (`eingang_ablegen` weicht aus, falls
        belegt); der Eintrag zeigt danach auf sie, die alte Datei wird entfernt.
        """
        job = Meshfotoendpunkte._job(job_id)
        if job.laeuft:
            return JsonResponse({'error': 'Der Auftrag rechnet gerade — erst anhalten'}, status=409)
        neu = request.FILES.get('bild')
        if neu is None or not Meshablage.ist_bild(neu.name):
            return JsonResponse({'error': 'Kein Bild (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei},
                                status=404)
        ablage = Meshablage(job.kennung)
        gespeichert = ablage.eingang_ablegen(neu)
        alt = bilder[stelle]
        bilder[stelle] = {**alt, 'datei': gespeichert, 'original': neu.name}
        Meshfotoendpunkte._vorbereitetes_loeschen(ablage, datei)
        Meshfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Mesh %s: Foto %s durch %s ersetzt', job.kennung, datei, gespeichert)
        return Meshfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def loeschen(request, job_id, datei):
        job = Meshfotoendpunkte._job(job_id)
        if job.laeuft:
            return JsonResponse({'error': 'Der Auftrag rechnet gerade — erst anhalten'}, status=409)
        bilder = [b for b in (job.bilder or []) if b.get('datei') != datei]
        if len(bilder) == len(job.bilder or []):
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei},
                                status=404)
        if not bilder:
            return JsonResponse({'error': 'Das letzte Foto lässt sich nicht entfernen'}, status=400)
        ablage = Meshablage(job.kennung)
        Meshfotoendpunkte._vorbereitetes_loeschen(ablage, datei)
        Meshfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Mesh %s: Foto %s entfernt', job.kennung, datei)
        return Meshfotoendpunkte._antwort(job)

    @staticmethod
    def _eingang_loeschen(ablage, datei):
        try:
            pfad = ablage.datei(Meshablage.EINGANG, datei)
        except ValueError:
            logger.warning('Eingangsfoto %s: kein gültiger Name', datei)
            return
        try:
            pfad.unlink(missing_ok=True)
        except OSError:
            logger.warning('Eingangsfoto %s ließ sich nicht löschen', pfad)
