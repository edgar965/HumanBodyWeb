# -*- coding: utf-8 -*-
"""Haarenginefotoendpunkte — die Bildauswahl eines Auftrags „Haar Engine".

Die Fotos sind die VORLAGEN der Iterationen. Die Endpunkte sind die von `Meshendpunkte` (Rolle, Gewicht,
Platz) und `Meshfotoendpunkte` (hinzufügen, ersetzen, entfernen), auf den eigenen Auftrag gelegt:

    POST /api/haarengine/<id>/fotos/                   (multipart: bilder)  → anhängen (Rolle „aus")
    POST /api/haarengine/<id>/foto/<datei>/ersetzen/   (multipart: bild)    → an Ort und Stelle
    POST /api/haarengine/<id>/foto/<datei>/loeschen/                        → entfernen
    POST /api/haarengine/<id>/rolle/<datei>/           {rolle}
    POST /api/haarengine/<id>/gewicht/<datei>/         {gewicht, bereich?}
    POST /api/haarengine/<id>/reihenfolge/             {datei, index}       (1-basiert)
    → {ok, bilder: [...]}

Hinzufügen, Ersetzen und Entfernen gehen auch während eines Laufs — ein laufender Kreislauf sieht die
Änderung ab dem nächsten Lauf. `Haarengineauftrag.bilder_sichern` schützt Rolle, Gewicht und Reihenfolge
gegen einen Lauf, der seinen alten Stand zurückschreibt. Nach jeder Änderung an Platz 1 wird das kleine
Vorlagenbild der Tabelle neu geschrieben (`Haarenginevorlage`).
"""

import logging

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.haarengineablage import Haarengineablage
from ..dienste.haarenginevorlage import Haarenginevorlage
from ..dienste.meshoptionen import Meshoptionen
from ..models import Haarengineauftrag
from .haarengine import Haarengineendpunkte

logger = logging.getLogger('core')

__all__ = ['Haarenginefotoendpunkte']


class Haarenginefotoendpunkte:
    @staticmethod
    def _job(job_id):
        return get_object_or_404(Haarengineauftrag, id=job_id)

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
    def _eingang_loeschen(ablage, datei):
        try:
            pfad = ablage.datei(Haarengineablage.EINGANG, datei)
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
        job = Haarenginefotoendpunkte._job(job_id)
        dateien = [f for f in request.FILES.getlist('bilder') if Haarengineablage.ist_bild(f.name)]
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        ablage = Haarengineablage(job.kennung)
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
        Haarenginevorlage.erneuern(job)
        logger.info('Haar Engine %s: %d Foto(s) hinzugefügt', job.kennung, len(dateien))
        return Haarenginefotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def ersetzen(request, job_id, datei):
        """Ein Foto austauschen — Rolle, Gewicht, Bereich und Platz bleiben; die neue Datei bekommt einen
        eigenen Namen, der Eintrag zeigt danach auf sie, die alte wird entfernt."""
        job = Haarenginefotoendpunkte._job(job_id)
        neu = request.FILES.get('bild')
        if neu is None or not Haarengineablage.ist_bild(neu.name):
            return JsonResponse({'error': 'Kein Bild (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        ablage = Haarengineablage(job.kennung)
        bilder[stelle] = {**bilder[stelle], 'datei': ablage.eingang_ablegen(neu), 'original': neu.name}
        Haarenginefotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Haarenginevorlage.erneuern(job)
        logger.info('Haar Engine %s: Foto %s ersetzt', job.kennung, datei)
        return Haarenginefotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def loeschen(request, job_id, datei):
        job = Haarenginefotoendpunkte._job(job_id)
        bilder = [b for b in (job.bilder or []) if b.get('datei') != datei]
        if len(bilder) == len(job.bilder or []):
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        if not bilder:
            return JsonResponse({'error': 'Das letzte Foto lässt sich nicht entfernen'}, status=400)
        ablage = Haarengineablage(job.kennung)
        Haarenginefotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Haarenginevorlage.erneuern(job)
        logger.info('Haar Engine %s: Foto %s entfernt', job.kennung, datei)
        return Haarenginefotoendpunkte._antwort(job)

    # ------------------------------------------ Rolle, Gewicht, Platz

    @staticmethod
    @require_POST
    def rolle(request, job_id, datei):
        job = Haarenginefotoendpunkte._job(job_id)
        eintrag = Haarenginefotoendpunkte._bild_oder_404(job, datei)
        eintrag['rolle'] = Meshoptionen.rolle_pruefen(Haarengineendpunkte.rumpf(request).get('rolle'))
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def gewicht(request, job_id, datei):
        """Fotogewicht (0..100) und optionaler Bereichsausschnitt — wirkt beim nächsten Lauf von „netz"."""
        job = Haarenginefotoendpunkte._job(job_id)
        eintrag = Haarenginefotoendpunkte._bild_oder_404(job, datei)
        rumpf = Haarengineendpunkte.rumpf(request)
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
        job = Haarenginefotoendpunkte._job(job_id)
        rumpf = Haarengineendpunkte.rumpf(request)
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
            Haarenginevorlage.erneuern(job)
        return Haarenginefotoendpunkte._antwort(job)
