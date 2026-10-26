# -*- coding: utf-8 -*-
"""Ai2d3dabnahmeendpunkte — die Abnahme eines Tests misst, was die JOBSEITE zeichnet (24.10.2026; Edgar: „unverändert schlecht. Passe deine testmethoden an, das musst du Doch selber
herausfinden, dass die nicht übereinstimmen“). Bis dahin renderte die Prüfung mit einem eigenen Python-Renderer (`Koerperbild`) — der kannte das Anatomie-Stück nicht und verdeckte die Haut
anders als die Seite: Die Prüfung sah Shorts bis zum Saum, die Seite zeigte Edgar ein Genital unter zu kurzen Shorts.

    GET  /api/2d3dai/<job>/abnahme/kameras/        die Kameras der Fotos aus der Einpassung (`<Job>/abnahme/kameras.json`, schreibt `koerperpruefung_lauf.py`)
    POST /api/2d3dai/<job>/abnahme/seite/<nr>/     {bild: 'data:image/png;base64,…'} — das Rendering der Seite aus der Kamera von Foto <nr> (`Ai2d3dseitenbild`), RGBA, Alpha = Figur
                                                   → `<Job>/abnahme/seite_<nr>.png`
    GET  /api/2d3dai/<job>/abnahme/seite/<nr>/     dieses Rendering (für die Testzeile „Messpunkte“)
    GET  /api/2d3dai/<job>/abnahme/haltungen/      Haltung je Foto der Testfigur (`Ai2d3dseitenbild` rendert jedes Foto in seiner Haltung)
    GET  /api/2d3dai/<job>/abnahme/messpunkte/     die Messpunkte von Foto und Rendering (`<Job>/abnahme/messpunkte.json`, `Koerpermesspunkte`), je Foto mit `veraltet`: das Rendering
                                                   ist neuer als die Messung (Seite neu aufgenommen, `koerperpruefung_lauf.py --seite` noch nicht gelaufen)
Nur für Tests aus Fotos (`art == 'foto'`).
"""
import base64
import json
import logging
from pathlib import Path

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from ..dienste.ai2d3djobs import Ai2d3djobs

logger = logging.getLogger('core')

__all__ = ['Ai2d3dabnahmeendpunkte']


class Ai2d3dabnahmeendpunkte:
    KOPF = 'data:image/png;base64,'
    #: größtes Bild (Bytes), weit über dem, was die Seite schickt (1.600 px hoch, gemessen ~1 MB)
    GRENZE = 12 * 1024 * 1024

    @staticmethod
    def _test(job):
        gefunden = Ai2d3djobs.job(job)
        return gefunden if gefunden is not None and gefunden.get('art') == 'foto' else None

    @staticmethod
    @require_GET
    def kameras(request, job):
        gefunden = Ai2d3dabnahmeendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        datei = Path(gefunden['ordner']) / 'abnahme' / 'kameras.json'
        if not datei.is_file():
            return JsonResponse({'error': 'Für %s liegen keine Kameras der Einpassung vor (%s) — erst koerperpruefung_lauf.py' % (job, datei)}, status=404)
        return JsonResponse(json.loads(datei.read_text(encoding='utf-8')))

    @staticmethod
    @require_GET
    def messpunkte(request, job):
        return Ai2d3dabnahmeendpunkte._messung(job, 'messpunkte.json')

    @staticmethod
    @require_GET
    def kopfmesspunkte(request, job):
        """Die Messpunkte des Kopfs (25.10.2026, `Kopfmesspunkte`) — eigene Testzeile unter der des Körpers, dieselbe Form."""
        return Ai2d3dabnahmeendpunkte._messung(job, 'kopfmesspunkte.json')

    @staticmethod
    @require_GET
    def reglermesspunkte(request, job):
        """Die Messlinien an den Anfassern der Eigenregler (25.10.2026 abends, `Reglermesspunkte`; Kennzeichen wie im Bedienfeld) — dritte Testzeile, dieselbe Form."""
        return Ai2d3dabnahmeendpunkte._messung(job, 'reglermesspunkte.json')

    @staticmethod
    @require_GET
    def reglerumrisse(request, job):
        """Die ganzen Umrisse der Eigenregler in Foto und Rendering (26.10.2026, `Reglerumrisse`) — vierte Testzeile, dieselbe Form plus `umrisse`."""
        return Ai2d3dabnahmeendpunkte._messung(job, 'reglerumrisse.json')

    @staticmethod
    @require_GET
    def gesichtspunkte(request, job, art=''):
        """Die 478 Gesichtspunkte von MediaPipe im Foto von vorn gegen dieselben Punkte an der Figur (26.10.2026, `Gesichtsmesspunkte`) — die Messung der Kopf-KI, dieselbe Form; mit `art`
        die Karten ihres Fehlers: `anker` (MediaPipe auf dem Rendering ↔ Netzstellen), `rendering` (MediaPipe am Foto ↔ auf dem Rendering)."""
        if art not in ('', 'anker', 'rendering'):
            return JsonResponse({'error': 'Keine Gesichtspunkte %s' % art}, status=404)
        return Ai2d3dabnahmeendpunkte._messung(job, 'gesichtspunkte%s.json' % ('_' + art if art else ''))

    #: Blöcke der aufgeräumten Seite (26.10.2026, `Abnahmebloecke`) — nur diese Namen, die Adresse wählt keine beliebige Datei
    BLOECKE = ('kopf_vorne', 'kopf_seitlich', 'koerper_vorne', 'koerper_seitlich')

    @staticmethod
    @require_GET
    def block(request, job, name):
        """Ein Block „Kopf/Körper vorne/seitlich“: Umrisse der Eigenregler und Gesichtsgruppen, dieselbe Form wie die Testzeilen."""
        if name not in Ai2d3dabnahmeendpunkte.BLOECKE:
            return JsonResponse({'error': 'Kein Block %s' % name}, status=404)
        return Ai2d3dabnahmeendpunkte._messung(job, 'block_%s.json' % name)

    @staticmethod
    @require_GET
    def ampel(request, job):
        """Die Ampel: je Eigenregler und Foto die mittlere Abweichung in mm (`Abnahmebloecke`)."""
        return Ai2d3dabnahmeendpunkte._messung(job, 'ampel.json')

    @staticmethod
    def _messung(job, name):
        gefunden = Ai2d3dabnahmeendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        ordner = Path(gefunden['ordner']) / 'abnahme'
        datei = ordner / name
        if not datei.is_file():
            return JsonResponse({'error': 'Für %s liegen keine Messpunkte vor — im Chrome window.__ai2d3d.seitenbilder(), dann koerperpruefung_lauf.py <stand> --seite' % job},
                                status=404)
        daten = json.loads(datei.read_text(encoding='utf-8'))
        for nr, f in daten.get('fotos', {}).items():
            bild = ordner / ('seite_%s.png' % nr)
            f['veraltet'] = not bild.is_file() or abs(bild.stat().st_mtime - f.get('seite_zeit', 0)) > 1
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def haltungen(request, job):
        """Haltung je Foto (Auftrag EdgarTrip, 24.10.2026: „Haltung je Foto, Form gemeinsam“): rig_<n>, dreh_<n> der Testfigur aus `ergebnis_Form_<g>.npz` des Mesh3D-AI-Tests
        (schreibt `nurfotos_koerper.py`) → {fotos: {Stamm des Fotos: {ausgabe, dreh (Quaternionen wie die Testschnittstelle)}}}; leer, wenn die Ablage nur eine Haltung trägt."""
        import numpy as np
        from django.conf import settings

        from ..dienste.mesh3daidaten import Mesh3daidaten
        gefunden = Ai2d3dabnahmeendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        # die eigene Figur des Jobs (`<Job>/figur/`, `Ai2d3dfigur`, 25.10.2026), sonst die Ablage des Mesh3D-AI-Tests
        from ..dienste.ai2d3dfigur import Ai2d3dfigur
        eigen = Ai2d3dfigur.ordner_von(gefunden)
        test = json.loads((Path(gefunden['ordner']) / 'job.json').read_text(encoding='utf-8')).get('mesh3dai_test')
        ablage = eigen or ((Path(settings.TOOLS_ROOT) / '3DObjects' / 'mesh3dai' / '_test' / str(test)) if test else None)
        dateien = sorted(ablage.glob('ergebnis_Form_*.npz')) if ablage else []
        if not dateien:
            return JsonResponse({'error': 'Für %s gibt es keine Ergebnisablage des Mesh3D-AI-Tests (%s)' % (job, test)}, status=404)
        fotos = {}
        with np.load(dateien[0]) as z:
            for k in z.files:
                if k.startswith('rig_') and 'dreh_' + k[4:] in z.files:
                    fotos[k[4:]] = {'ausgabe': np.round(z[k].astype(float), 4).tolist(), 'dreh': np.round(Mesh3daidaten._quaternionen(z['dreh_' + k[4:]].astype(float)), 5).tolist()}
        return JsonResponse({'quelle': str(dateien[0]), 'zeit': dateien[0].stat().st_mtime, 'fotos': fotos})

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def seite(request, job, nr):
        gefunden = Ai2d3dabnahmeendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        if request.method == 'GET':
            bild = Path(gefunden['ordner']) / 'abnahme' / ('seite_%d.png' % int(nr))
            if not bild.is_file():
                return JsonResponse({'error': 'Kein Rendering der Seite für Foto %d (%s)' % (int(nr), bild)}, status=404)
            return FileResponse(open(bild, 'rb'), content_type='image/png')
        try:
            bild = json.loads(request.body or b'{}').get('bild') or ''
        except (ValueError, AttributeError):
            return JsonResponse({'error': 'Rumpf ist kein JSON mit bild'}, status=400)
        if not bild.startswith(Ai2d3dabnahmeendpunkte.KOPF):
            return JsonResponse({'error': 'bild ist kein PNG als data-URL'}, status=400)
        roh = base64.b64decode(bild[len(Ai2d3dabnahmeendpunkte.KOPF):])
        if not roh.startswith(b'\x89PNG') or len(roh) > Ai2d3dabnahmeendpunkte.GRENZE:
            return JsonResponse({'error': 'kein PNG oder zu groß (%d Bytes)' % len(roh)}, status=400)
        ziel = Path(gefunden['ordner']) / 'abnahme' / ('seite_%d.png' % int(nr))
        ziel.parent.mkdir(exist_ok=True)
        neben = ziel.with_suffix('.png.neu')
        neben.write_bytes(roh)
        neben.replace(ziel)
        logger.info('2d-3d-AI Abnahme %s: Rendering der Seite für Foto %d abgelegt (%d Bytes)', gefunden['id'], int(nr), len(roh))
        return JsonResponse({'ok': True, 'datei': str(ziel), 'bytes': len(roh)})
