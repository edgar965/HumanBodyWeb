# -*- coding: utf-8 -*-
"""Blendimportbegriffe — Bestandteile des Netzes über Textbegriffe: SAM 3 an den Ansichten der Segmentierung (12.10.2026).

Edgar am Zauberer: „der Bart fehlt, … der Stab wird nicht erkannt" und, als ich dafür eine Suchklasse nur für Stangen baute: „ich möchte nicht für jedes Modell eine eigene Suchklasse machen … einen generischen
Code, der solche Sachen beim nächsten Mal automatisch erkennt." Sapiens trennt 28 feste Klassen (kein Stab, kein Bart, keine Tasche); SAM 3 findet jeden Begriff, den man als Text gibt (`sam3_begriffe.py`). Dieser Schritt
läuft in der Segmentierung des Wegs „netz" nach Sapiens, mit denselben Renderings und demselben Abstimm-Netz, und schreibt `teile_flaechen.npz` (Stimmen je Fläche und Begriff). Der Vorrat der Begriffe
ist eine Datei (`Kleidung/begriffsvorrat.json`) — ein neuer Gegenstand ist eine neue Zeile.

Was daraus wird (Flächen → Bestandteile, Bewegung in die Ruhelage, Objekte): `Kleidung/bestandteile.py`, `Meshfigurteile`. Der Schritt ist ein Zusatz: scheitert er, steht der Grund im Bericht, die
Segmentierung und „Mesh to 3D" laufen wie vorher.
"""

import json
import logging
import os

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from ..pipeline_process import PipelineProzess, PipelineStille

logger = logging.getLogger('core')

__all__ = ['Blendimportbegriffe']


class Blendimportbegriffe:
    RUNNER = '_run_sam3teile.py'
    DATEI = 'teile_flaechen.npz'
    #: Modell laden und vier Ansichten mit zwölf Begriffen: gemessen (Probe) wenige Sekunden je Ansicht; das Laden der 3,4 GB dauert am längsten.
    STILLE_S = 900

    def __init__(self, segmentierung):
        """`segmentierung`: die `Blendimportsegmentierung`, deren Renderings, Abstimm-Netz und Ordner dieser Schritt mitbenutzt."""
        self.s = segmentierung
        self.ergebnis = None

    @staticmethod
    def vorrat():
        """`[{phrase, gruppe}]` aus `Kleidung/begriffsvorrat.json`."""
        with open(settings.BEGRIFFSVORRAT, encoding='utf-8') as datei:
            return json.load(datei)['begriffe']

    def ausfuehren(self):
        """Rechnet die Begriffe und gibt den Bericht (`{begriffe: {phrase: {treffer, bestwert, flaechen, cm2}}, bilder, flaechen, sekunden}`) oder `{'fehler': …}` zurück — wirft nie außer beim Anhalten."""
        s = self.s
        # Eine Datei eines früheren Laufs darf nie stehen bleiben, wenn dieser scheitert: `_uebertragen` stempelte sie sonst auf das neue Netz (`artefakte-benennen.md`).
        for ordner in {s.ordner(), s._arbeit}:
            (ordner / self.DATEI).unlink(missing_ok=True)
        try:
            auftrag = s.ordner() / 'sam3_auftrag.json'
            auftrag.write_text(json.dumps({
                'kennung': s.ablage.kennung, 'netz': str(s._netz), 'bilder': s._bilder, 'begriffe': self.vorrat(), 'klon': str(settings.SAM3DBODY_KLON),
                'checkpoint': str(settings.SAM3_CHECKPOINT), 'raster': int((s.optionen or {}).get('raster') or 0) or None,
                'ordner': {'segmentierung': str(s.ordner()), 'arbeit': str(s._arbeit)},
            }, ensure_ascii=False, indent=1), encoding='utf-8')
            runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
            tmp = s.ordner() / 'tmp'
            tmp.mkdir(parents=True, exist_ok=True)
            pp = PipelineProzess.starten([settings.SAM3DBODY_PYTHON, '-I', runner, str(auftrag)], cwd=Wrapperpfad.pfad(),
                                         env_extra={'PYTHONIOENCODING': 'utf-8', 'HF_HOME': str(settings.HF_HOME_DIR), 'TMP': str(tmp), 'TEMP': str(tmp)})
            logger.info('Mesh-3D %s: SAM-3-Runner %s gestartet', s.ablage.kennung, pp.proc.pid)
            try:
                for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                    self._zeile(zeile.rstrip('\n'))
                    if s.lauf.angehalten():
                        pp.beenden()
                        raise s.lauf.Angehalten()
            except PipelineStille as fehler:
                pp.beenden()
                raise RuntimeError('SAM-3-Runner schweigt (%s)' % fehler) from fehler
            rc = pp.warten(timeout=120)
            if rc != 0 or self.ergebnis is None:
                raise RuntimeError('SAM-3-Runner endete mit %s: %s' % (rc, pp.fehlertext(1500) or 'ohne Meldung'))
            return self.ergebnis
        except s.lauf.Angehalten:
            raise
        except Exception as fehler:  # noqa: BLE001 — ein Zusatz: Segmentierung und „Mesh to 3D" laufen wie vorher, der Grund steht im Bericht
            logger.exception('Mesh-3D %s: Bestandteile (SAM 3) gescheitert', s.ablage.kennung)
            return {'fehler': str(fehler)[:300]}

    def _zeile(self, zeile):
        if zeile.startswith('[fortschritt] '):
            teile = zeile[len('[fortschritt] '):].split(' ', 1)
            try:
                wert = max(0, min(99, int(float(teile[0]))))
            except ValueError:
                return
            # Das Band 0,88–0,96 der Segmentierung (Sapiens hat 0,1–0,88, das Übertragen 0,97).
            self.s.lauf.melden(0.88 + 0.08 * wert / 100.0, 'Bestandteile: ' + (teile[1] if len(teile) > 1 else ''))
        elif zeile.startswith('[ergebnis] '):
            try:
                self.ergebnis = json.loads(zeile[len('[ergebnis] '):])
            except ValueError:
                logger.error('Mesh-3D %s: Ergebniszeile von SAM 3 nicht lesbar: %.200s', self.s.ablage.kennung, zeile)
