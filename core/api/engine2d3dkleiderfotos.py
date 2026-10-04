# -*- coding: utf-8 -*-
"""Engine2d3dKleiderfotoendpunkte — die Bildauswahl eines Auftrags „2D3D Kleider".

Die Fotos sind die VORLAGEN der Iterationen. Die Endpunkte sind die von `Meshendpunkte` (Rolle, Gewicht,
Platz) und `Meshfotoendpunkte` (hinzufügen, ersetzen, entfernen), auf den eigenen Auftrag gelegt:

    POST /api/engine2d3dkleider/<id>/fotos/                   (multipart: bilder)  → anhängen (Rolle „aus")
    POST /api/engine2d3dkleider/<id>/foto/<datei>/ersetzen/   (multipart: bild)    → an Ort und Stelle
    POST /api/engine2d3dkleider/<id>/foto/<datei>/loeschen/                        → entfernen
    POST /api/engine2d3dkleider/<id>/rolle/<datei>/           {rolle}
    POST /api/engine2d3dkleider/<id>/gewicht/<datei>/         {gewicht, bereich?}
    POST /api/engine2d3dkleider/<id>/reihenfolge/             {datei, index}       (1-basiert)
    → {ok, bilder: [...]}

Hinzufügen, Ersetzen und Entfernen gehen auch während eines Laufs — ein laufender Kreislauf sieht die
Änderung ab dem nächsten Lauf. `Engine2d3dKleiderauftrag.bilder_sichern` schützt Rolle, Gewicht und Reihenfolge
gegen einen Lauf, der seinen alten Stand zurückschreibt. Nach jeder Änderung an Platz 1 wird das kleine
Vorlagenbild der Tabelle neu geschrieben (`Engine2d3dKleidervorlage`).
"""

import logging

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.engine2d3dkleiderrollen import Engine2d3dKleiderrollen
from ..dienste.engine2d3dkleidervorlage import Engine2d3dKleidervorlage
from ..dienste.meshoptionen import Meshoptionen
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderfotoendpunkte']


class Engine2d3dKleiderfotoendpunkte:
    @staticmethod
    def _job(job_id):
        return get_object_or_404(Engine2d3dKleiderauftrag, id=job_id)

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
            pfad = ablage.datei(Engine2d3dKleiderablage.EINGANG, datei)
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
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        dateien = [f for f in request.FILES.getlist('bilder') if Engine2d3dKleiderablage.ist_bild(f.name)]
        if not dateien:
            return JsonResponse({'error': 'Keine Bilder (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        ablage = Engine2d3dKleiderablage(job.kennung)
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
        Engine2d3dKleidervorlage.erneuern(job)
        logger.info('2D3D Kleider %s: %d Foto(s) hinzugefügt', job.kennung, len(dateien))
        return Engine2d3dKleiderfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def ersetzen(request, job_id, datei):
        """Ein Foto austauschen — Rolle, Gewicht, Bereich und Platz bleiben; die neue Datei bekommt einen
        eigenen Namen, der Eintrag zeigt danach auf sie, die alte wird entfernt."""
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        neu = request.FILES.get('bild')
        if neu is None or not Engine2d3dKleiderablage.ist_bild(neu.name):
            return JsonResponse({'error': 'Kein Bild (JPG, PNG, WebP, BMP, TIFF)'}, status=400)
        bilder = list(job.bilder or [])
        stelle = next((i for i, b in enumerate(bilder) if b.get('datei') == datei), None)
        if stelle is None:
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        ablage = Engine2d3dKleiderablage(job.kennung)
        bilder[stelle] = {**bilder[stelle], 'datei': ablage.eingang_ablegen(neu), 'original': neu.name}
        Engine2d3dKleiderfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Engine2d3dKleidervorlage.erneuern(job)
        logger.info('2D3D Kleider %s: Foto %s ersetzt', job.kennung, datei)
        return Engine2d3dKleiderfotoendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def loeschen(request, job_id, datei):
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        bilder = [b for b in (job.bilder or []) if b.get('datei') != datei]
        if len(bilder) == len(job.bilder or []):
            return JsonResponse({'error': 'Foto „%s" gehört nicht zu diesem Auftrag' % datei}, status=404)
        if not bilder:
            return JsonResponse({'error': 'Das letzte Foto lässt sich nicht entfernen'}, status=400)
        ablage = Engine2d3dKleiderablage(job.kennung)
        Engine2d3dKleiderfotoendpunkte._eingang_loeschen(ablage, datei)
        job.bilder = bilder
        job.save(update_fields=['bilder', 'updated_at'])
        Engine2d3dKleidervorlage.erneuern(job)
        logger.info('2D3D Kleider %s: Foto %s entfernt', job.kennung, datei)
        return Engine2d3dKleiderfotoendpunkte._antwort(job)

    # ------------------------------------------ Rolle, Gewicht, Platz

    @staticmethod
    @require_POST
    def rolle(request, job_id, datei):
        """Rolle eines Fotos (auch „Nur Iterationen", `Engine2d3dKleiderrollen`) und, wenn mitgeschickt, sein Blickwinkel in Grad
        ab vorn (`winkel`, positiv zur linken Seite der Figur; leer = die Pose schätzt ihn)."""
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        eintrag = Engine2d3dKleiderfotoendpunkte._bild_oder_404(job, datei)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        eintrag['rolle'] = Engine2d3dKleiderrollen.pruefen(rumpf.get('rolle'))
        if 'winkel' in rumpf:
            # Immer als Schlüssel (auch None): `bilder_sichern` übernimmt Nutzerfelder nur, wo sie in der Datenbank stehen.
            eintrag['winkel'] = Engine2d3dKleiderrollen.winkel_pruefen(rumpf.get('winkel'))
        if 'farbe' in rumpf:
            eintrag['farbe'] = Engine2d3dKleiderrollen.farbe_pruefen(rumpf.get('farbe')) is not False
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'bild': eintrag})

    @staticmethod
    @require_POST
    def gewicht(request, job_id, datei):
        """Fotogewicht (0..100) und optionaler Bereichsausschnitt — wirkt beim nächsten Lauf von „netz"."""
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        eintrag = Engine2d3dKleiderfotoendpunkte._bild_oder_404(job, datei)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
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
        job = Engine2d3dKleiderfotoendpunkte._job(job_id)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
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
            Engine2d3dKleidervorlage.erneuern(job)
        return Engine2d3dKleiderfotoendpunkte._antwort(job)
