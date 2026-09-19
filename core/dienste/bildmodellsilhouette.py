# -*- coding: utf-8 -*-
"""Bildmodellsilhouette — die SMPL-X-Form je Hauptbild an die Personenmaske.

Edgar (19.09.2026, „baue alles"): Silhouettenabgleich. `_run_silhouette.py`
(python10, pytorch3d, YOLO11-Seg) stellt Betas und Kameraverschiebung
jeder SMPLest-X-Schätzung so nach, dass die projizierte Silhouette die
Maske trifft — Pose und Brennweite bleiben. Gemessen an Damiras zwei
Vorderansichten: IoU 0,819 → 0,869 und 0,824 → 0,893, das Netz aus den
Parametern trifft das gespeicherte auf 0,0 mm (Gegenprobe), 5 s je Bild.
Sichtprobe `ProjektTemp/silhouette_probe/sicht_*.png`: die rohe Silhouette
stand seitlich versetzt und zu breit; danach bleibt nur der Haarknoten.

Nur SMPLest-X: PyMAF-X' Kameramodell (`kamera_pymafx`) ist nicht gegen
ein gespeichertes Netz geprüft. Die rohen Betas bleiben als `betas_roh`
am Eintrag, `silhouette` trägt die Zahlen für die Kachel.

WAHRHEITSPROBE (`ProjektTemp/silhouette_wahrheit.py`, Ursula gerendert,
vorn + hinten, SMPLest-X → Zielnetz → Anpassung ohne Ursulas Regler,
Käfig gegen Ursulas echten Käfig): roh 9,75 mm RMS; mit Abgleich 10,90
(Kamera frei, Strafe 0,02), 11,30 (Kamera fest, 0,02), 10,34 (0,2), 9,90
(1,0) — die IoU steigt (0,81 → 0,88), die FORM wird schlechter: die Betas
gleichen Pose- und Projektionsfehler aus, nicht Formfehler. Darum:
`silhouette` = `aus` (Vorgabe) oder `messen` (IoU als Kennzahl je Bild,
Betas bleiben roh) — `an` ersetzt die Betas, mit diesem Befund im Katalog.
"""

import json
import logging
import os
import subprocess

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellmehrbild import Bildmodellmehrbild

logger = logging.getLogger('core')

__all__ = ['Bildmodellsilhouette']


class Bildmodellsilhouette:
    RUNNER = '_run_silhouette.py'
    AUFTRAG = 'silhouette.json'
    WARTEZEIT = 3600
    BACKENDS = ('smplest_x',)

    def __init__(self, ablage):
        self.ablage = ablage

    @classmethod
    def offen(cls, bilder):
        """Einträge mit Pose und Kamera, die noch keinen Abgleich haben."""
        aus = []
        for b in bilder:
            s = b.get('schaetzung') or {}
            if s.get('backend') not in cls.BACKENDS or s.get('fehler'):
                continue
            if s.get('silhouette') and 'fehler' not in s['silhouette']:
                continue
            if s.get('pose') and s.get('cam_focal') and s.get('processed_bbox'):
                aus.append(b)
        return aus

    def auftrag(self, bilder):
        eintraege = []
        for b in bilder:
            s = b['schaetzung']
            posed = s.get('posed_vertices_path')
            eintraege.append({
                'datei': str(self.ablage.zuschnitt() / b['datei']),
                'schaetzung': s,
                'posed': str(self.ablage.schaetzung() / posed) if posed else None,
            })
        pfad = self.ablage.schaetzung() / self.AUFTRAG
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump({'bilder': eintraege}, f)
        return pfad

    @staticmethod
    def zuruecksetzen(bilder):
        """Die rohen Betas zurück, wenn ein früherer Lauf sie ersetzt hatte."""
        for b in bilder:
            s = b.get('schaetzung') or {}
            if s.get('betas_roh'):
                s['betas'] = s.pop('betas_roh')
            if s.get('cam_trans_roh'):
                s['cam_trans'] = s.pop('cam_trans_roh')

    def ausfuehren(self, bilder, melder=None, ersetzen=True):
        """Abgleich über alle `bilder`; schreibt `silhouette` an die Einträge und —
        mit `ersetzen` — Betas und Verschiebung."""
        if not bilder:
            return 0
        if melder:
            melder(0.9, 'Silhouettenabgleich (%d Bilder)' % len(bilder))
        pfad = self.auftrag(bilder)
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, os.path.join(Wrapperpfad.pfad(), self.RUNNER), str(pfad)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Silhouette: keine Antwort nach %d s' % self.WARTEZEIT) from None
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort or 'error' in antwort:
            raise RuntimeError('Silhouette: %s' % ((antwort or {}).get('error') or (fehler or '')[-400:]))
        nach_datei = {e.get('datei'): e for e in antwort.get('bilder', [])}
        n = 0
        for b in bilder:
            e = nach_datei.get(b['datei']) or {'error': 'keine Antwort'}
            s = b['schaetzung']
            if 'error' in e:
                s['silhouette'] = {'fehler': str(e['error'])}
                continue
            if ersetzen:
                s['betas_roh'] = list(s.get('betas') or [])
                s['betas'] = e['betas']
                s['cam_trans_roh'] = list(s.get('cam_trans') or [])
                s['cam_trans'] = e['cam_trans']
            s['silhouette'] = {
                k: e.get(k) for k in ('iou_vorher', 'iou_nachher', 'guete_maske', 'netzabweichung_mm')
            }
            n += 1
        logger.info('Bildmodell: Silhouettenabgleich an %d von %d Bildern', n, len(bilder))
        return n
