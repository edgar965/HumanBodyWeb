# -*- coding: utf-8 -*-
"""Blendermodellfotoendpunkte — die Bildauswahl eines Auftrags „BlenderModel" (29.09.2026).

Edgar: „Im Job soll es eine Bildauswahl geben wie in [Mesh-Auftrag]". Die Endpunkte sind die von
`Meshendpunkte` (Rolle, Gewicht, Platz) und `Meshfotoendpunkte` (hinzufügen, ersetzen, entfernen),
auf den eigenen Auftrag gelegt:

    POST /api/blendermodell/<id>/fotos/                   (multipart: bilder)  → anhängen (Rolle „aus")
    POST /api/blendermodell/<id>/foto/<datei>/ersetzen/   (multipart: bild)    → an Ort und Stelle
    POST /api/blendermodell/<id>/foto/<datei>/loeschen/                        → entfernen
    POST /api/blendermodell/<id>/rolle/<datei>/           {rolle}
    POST /api/blendermodell/<id>/gewicht/<datei>/         {gewicht, bereich?}
    POST /api/blendermodell/<id>/reihenfolge/             {datei, index}       (1-basiert)
    → {ok, bilder: [...]}

**Die vorbereitete Fassung muss mit weg:** `vorbereitet/<stamm>.png` ist das freigestellte, lichtausgeglichene
Foto aus einem früheren Lauf. Der Runner verwendet es wieder, wenn es da ist — ein ersetztes Foto würde sonst
still ignoriert und der nächste Lauf rechnete mit dem alten Bild weiter.

Hinzufügen, Ersetzen und Entfernen gehen auch während eines Laufs (Edgar, 29.09.2026: „die sollen nicht
gesperrt sein beim Lauf") — die Fotos sind hier nur Referenz für den Bau, kein Live-Eingang eines Netz-
Schritts mehr. `Blendermodellauftrag.bilder_sichern` schützt Rolle, Gewicht und Reihenfolge gegen einen
Lauf, der seinen alten Stand zurückschreibt.

Nach jeder Änderung an Platz 1 wird das kleine Vorlagenbild der Tabelle neu geschrieben
(`Blendermodellvorlage`).
"""

import logging
import os

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.blendermodellablage import Blendermodellablage
from ..dienste.blendermodellvorlage import Blendermodellvorlage
from ..dienste.meshoptionen import Meshoptionen
from ..models import Blendermodellauftrag
from .blendermodell import Blendermodellendpunkte

logger = logging.getLogger('core')

__all__ = ['Blendermodellfotoendpunkte']


class Blendermodellfotoendpunkte:
    @staticmethod
    def _job(job_id):
        return get_object_or_404(Blendermodellauftrag, id=job_id)

    @staticmethod
    def _antwort(job):
        return JsonResponse({'ok': True, 'bilder': job.bilder})

    @staticmethod
    def _bild_oder_404(job, datei):
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        return eintrag

    @staticmethod
    def _vorbereitetes_loeschen(ablage, datei):
        """Die freigestellte Fassung eines Fotos verwerfen (siehe Kopf der Datei)."""
        stamm = os.path.splitext(str(datei))[0]
        ordner = ablage.unter(Blendermodellablage.VORBEREITET)
        if not ordner.is_dir():
            return
        for pfad in ordner.glob(stamm + '.*'):
            try:
                pfad.unlink()
            except OSError:
                logger.warning('Vorbereitetes Foto %s ließ sich nicht löschen', pfad)

    @staticmethod
    def _eingang_loeschen(ablage, datei):
        try:
            pfad = ablage.datei(Blendermodellablage.EINGANG, datei)
        except ValueError:
            logger.warning('Eingangsfoto %s: kein gültiger Name', datei)
            return
        try:
            pfad.unlink(missing_ok=True)
        except OSError:
            logger.warning('Eingangsfoto %s ließ sich nicht löschen', pfad)

    # ------------------------------------------------- Fotos austauschen

    @staticmethod
    @require_POST
    def hinzufuegen(request, job_id):
        job = Blendermodellfotoendpunkte._job(job_id)
        dateien = [f for f in request.FILES.getlist('bilder') if Blendermodellablage.ist_bild(f.name)]
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        ablage = Blendermodellablage(job.kennung)
        bilder = list(job.bilder or [])
        for hochgeladen in dateien:
            bilder.append(
                {
                    'datei': ablage.eingang_ablegen(hochgeladen),
                    'original': hochgeladen.name,
                    'gewicht': 100,
                    'bereich': None,
                    'rolle': 'aus',
                }
            )
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Blendermodellvorlage.erneuern(job)
        logger.info('BlenderModel %s: %d Foto(s) hinzugefügt', job.kennung, len(dateien))
        return Blendermodellfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def ersetzen(request, job_id, datei):
        """Ein Foto austauschen — Rolle, Gewicht, Bereich und Platz bleiben; die neue Datei bekommt einen
        eigenen Namen, der Eintrag zeigt danach auf sie, die alte wird entfernt."""
        job = Blendermodellfotoendpunkte._job(job_id)
        neu = request.FILES.get('bild')
        if neu is None or not Blendermodellablage.ist_bild(neu.name):
            return JsonResponse({'error': 'Kein Bild (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        ablage = Blendermodellablage(job.kennung)
        bilder[stelle] = {**bilder[stelle], 'datei': ablage.eingang_ablegen(neu), 'original': neu.name}
        Blendermodellfotoendpunkte._vorbereitetes_loeschen(ablage, datei)
        Blendermodellfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Blendermodellvorlage.erneuern(job)
        logger.info('BlenderModel %s: Foto %s ersetzt', job.kennung, datei)
        return Blendermodellfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def loeschen(request, job_id, datei):
        job = Blendermodellfotoendpunkte._job(job_id)
        bilder = [b for b in (job.bilder or []) if b.get('datei') != datei]
        if len(bilder) == len(job.bilder or []):
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        if not bilder:
            return JsonResponse({'error': 'Das letzte Foto lässt sich nicht entfernen'}, status=400)
        ablage = Blendermodellablage(job.kennung)
        Blendermodellfotoendpunkte._vorbereitetes_loeschen(ablage, datei)
        Blendermodellfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Blendermodellvorlage.erneuern(job)
        logger.info('BlenderModel %s: Foto %s entfernt', job.kennung, datei)
        return Blendermodellfotoendpunkte._antwort(job)

    # ------------------------------------------ Rolle, Gewicht, Platz

    @staticmethod
    @require_POST
    def rolle(request, job_id, datei):
        job = Blendermodellfotoendpunkte._job(job_id)
        eintrag = Blendermodellfotoendpunkte._bild_oder_404(job, datei)
        eintrag['rolle'] = Meshoptionen.rolle_pruefen(Blendermodellendpunkte.rumpf(request).get('rolle'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def gewicht(request, job_id, datei):
        """Fotogewicht (0..100) und optionaler Bereichsausschnitt — wirkt beim nächsten Lauf von „netz"."""
        job = Blendermodellfotoendpunkte._job(job_id)
        eintrag = Blendermodellfotoendpunkte._bild_oder_404(job, datei)
        rumpf = Blendermodellendpunkte.rumpf(request)
        eintrag['gewicht'] = Meshoptionen.gewicht_pruefen(rumpf.get('gewicht'))
        if 'bereich' in rumpf:
            eintrag['bereich'] = Meshoptionen.bereich_pruefen(rumpf.get('bereich'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def reihenfolge(request, job_id):
        """Ein Foto an eine andere Stelle schieben; `index` ist 1-basiert wie im Feld „Platz". Platz 1 ist die
        „Vorlage" der Tabelle.

        NICHT `bilder_sichern()`: Das übernimmt die Reihenfolge aus der Datenbank (Schutz gegen einen
        Lauf, der seine alte Ordnung zurückschreibt) und hätte genau die Änderung verworfen, die der
        Aufruf bewirken soll (erst im Browser aufgefallen: 200 und keine Wirkung, `auftragsseiten.md`).
        """
        job = Blendermodellfotoendpunkte._job(job_id)
        rumpf = Blendermodellendpunkte.rumpf(request)
        datei = str(rumpf.get('datei') or '')
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            ziel = int(rumpf.get('index'))
        except TypeError, ValueError:
            return JsonResponse({'error': 'index fehlt oder ist keine Zahl'}, status=400)
        ziel = max(0, min(len(bilder) - 1, ziel - 1))
        vorher = bilder[0].get('datei')
        bilder.insert(ziel, bilder.pop(stelle))
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        if bilder[0].get('datei') != vorher:
            Blendermodellvorlage.erneuern(job)
        return Blendermodellfotoendpunkte._antwort(job)
