# -*- coding: utf-8 -*-
"""Posebestimmung — SAM 3D Body am Bild einer Person und die Gelenke im Netz, für JEDEN Lauf, der eine Pose braucht (11.10.2026).

Aus `Engine2d3dKleiderpose` herausgelöst, als der Import (`Blendimportpose`, Jobseite „Mesh-3D“) denselben Weg brauchte: ein Bild der Person (ein Foto oder ein Rendering des
Körpers) geht durch den Runner `_run_sam3dpose.py` (python12, SAM 3D Body) in vier Drehungen; die Gelenke der gewählten Drehung werden in die Silhouette des Netzes gelegt
(`Engine2d3dKleiderposeabbildung`) und als `landmarken.npz` (`roh` (33, 3), `treffer` (33)) abgelegt — das Format, das `Meshfigurerkennungsschritt` über `auftrag['landmarken_hand']` liest.

Die Klasse kennt weder Auftrag noch Schritt: Sie bekommt einen Ordner (`pose/`), `melden(anteil, text)` und `angehalten()` und gibt Wörterbücher zurück. Ablage und Ergebnisfeld gehören dem Aufrufer.
Der Lauf von SAM ist an Bild, Fassung und Drehungen gebunden (`sam3d.json`, `artefakte-benennen.md`): dieselben Gelenke werden nicht neu gerechnet, wenn nur die Drehung oder die Auswahl wechselt.
"""

import json
import logging
import os

import numpy as np
from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from ..pipeline_process import PipelineProzess, PipelineStille
from .engine2d3dkleiderposeabbildung import Engine2d3dKleiderposeabbildung
from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke

logger = logging.getLogger('core')

__all__ = ['Posebestimmung']


class Posebestimmung:
    RUNNER = '_run_sam3dpose.py'
    #: Das Modell laden meldet nichts zwischen 2 % und 40 %; SAM 3D Body braucht dafür 27–85 s.
    STILLE_S = 1800
    DREHUNGEN = (0, 90, 180, 270)
    #: Die Fassung der Ablage `sam3d.json` — eine andere gilt nie als aktuell.
    FASSUNG = 1
    #: Anteil des Fortschritts, den SAM belegt (der Rest gehört dem Aufrufer: Abbildung, Bilder).
    ANTEIL_SAM = 0.6

    def __init__(self, ordner, bezeichnung, melden, angehalten=lambda: False, abbrechen=RuntimeError):
        """`ordner`: Pfad (`pathlib.Path`) des Ordners `pose/`; `bezeichnung` für das Log; `abbrechen`: die Ausnahme, die bei `angehalten()` fliegt."""
        self.ordner = ordner
        self.bezeichnung = bezeichnung
        self.melden = melden
        self.angehalten = angehalten
        self.abbrechen = abbrechen

    @staticmethod
    def stand(pfad):
        s = os.stat(str(pfad))
        return [s.st_size, s.st_mtime_ns]

    # ------------------------------------------------------------- SAM 3D Body

    def sam(self, png, drehungen=DREHUNGEN, schluessel=None):
        """`(sam3d.json als dict, neu_gerechnet)` — aus der Ablage, wenn Bild, Fassung und Drehungen stimmen, sonst rechnet der Runner (python12).

        `schluessel` (JSON-fähig) ersetzt den Stempel der Bilddatei, wenn das Bild bei jedem Lauf neu gerendert wird (`Mesh3dansicht.eingaben`): seine Dateizeit ändert sich dann jedes Mal, und SAM rechnete
        jedes Mal neu (40 s am Zauberer, `sam_neu_gerechnet` war in jedem Lauf wahr)."""
        self.ordner.mkdir(parents=True, exist_ok=True)
        datei = self.ordner / 'sam3d.json'
        quelle = self.stand(png) if schluessel is None else schluessel
        try:
            alt = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            alt = None
        if alt and alt.get('fassung') == self.FASSUNG and alt.get('quelle') == quelle and all(str(g) in alt.get('drehungen', {}) for g in drehungen):
            return alt, False
        auftrag = self.ordner / 'auftrag.json'
        auftrag.write_text(json.dumps({
            'bild': str(png), 'ausgabe': str(datei), 'drehungen': list(drehungen), 'hf_home': str(settings.HF_HOME_DIR), 'klon': str(settings.SAM3DBODY_KLON),
            'checkpoint': str(settings.SAM3DBODY_CHECKPOINT), 'mhr': str(settings.SAM3DBODY_MHR),
        }, ensure_ascii=False, indent=1), encoding='utf-8')
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        tmp = self.ordner / 'tmp'
        tmp.mkdir(parents=True, exist_ok=True)
        pp = PipelineProzess.starten([settings.SAM3DBODY_PYTHON, '-I', runner, str(auftrag)], cwd=Wrapperpfad.pfad(),
                                     env_extra={'PYTHONIOENCODING': 'utf-8', 'HF_HOME': str(settings.HF_HOME_DIR), 'TMP': str(tmp), 'TEMP': str(tmp)})
        logger.info('%s: SAM-3D-Body-Runner %s gestartet', self.bezeichnung, pp.proc.pid)
        fertig = False
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                fertig = self._zeile(zeile.rstrip('\n')) or fertig
                if self.angehalten():
                    raise self.abbrechen()
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('SAM-3D-Body-Runner schweigt (%s)' % fehler) from fehler
        except BaseException:
            pp.beenden()
            raise
        rc = pp.warten(timeout=120)
        if rc != 0 or not fertig:
            raise RuntimeError('SAM-3D-Body-Runner endete mit %s: %s' % (rc, pp.fehlertext(1500) or 'ohne Meldung'))
        sam = json.loads(datei.read_text(encoding='utf-8'))
        sam.update(fassung=self.FASSUNG, quelle=quelle)
        datei.write_text(json.dumps(sam), encoding='utf-8')
        return sam, True

    def _zeile(self, zeile):
        """Fortschritt melden; `True` bei der Ergebniszeile."""
        if zeile.startswith('[fortschritt] '):
            teile = zeile[len('[fortschritt] '):].split(' ', 1)
            try:
                wert = max(0, min(99, int(float(teile[0]))))
            except ValueError:
                return False
            self.melden(self.ANTEIL_SAM * wert / 100.0, 'Pose: ' + (teile[1] if len(teile) > 1 else ''))
        return zeile.startswith('[ergebnis] ')

    # --------------------------------------------------------------- Abbildung

    def abbilden(self, netz, png, sam, grad, weglassen=(), masstab=False):
        """Die Gelenke der Drehung `grad` ins Netz: `{abbildung, scan, alpha, roh, treffer, liste, masstab}`; schreibt `landmarken.npz`.
        `netz`: Datei (GLB/OBJ …), die `Meshfigurscan` liest; `png`: das Bild, auf dem das Netz liegt (RGBA, Alpha = Person)."""
        from PIL import Image

        from ..daten.meshto3dpfad import Meshto3dpfad

        e = sam['drehungen'].get(str(grad)) or {}
        if 'k2' not in e:
            raise RuntimeError('SAM 3D Body hat in der Drehung %d° nichts geliefert (%s)' % (grad, e.get('fehler') or 'keine Ausgabe'))
        weglassen = tuple(weglassen)
        with Meshto3dpfad():
            from meshfigur_scan import Meshfigurscan
            scan = Meshfigurscan.laden(netz)
        alpha = np.asarray(Image.open(png).convert('RGBA'))[:, :, 3]
        abbildung = Engine2d3dKleiderposeabbildung(scan, alpha)
        roh, treffer, liste = abbildung.landmarken(np.asarray(e['k2']), sam['namen'], Engine2d3dKleiderposegelenke.ZUORDNUNG, weglassen)
        if int((treffer > 0).sum()) < 4:
            raise RuntimeError('Zu wenige Gelenke im Netz (%d) — Drehung oder Auswahl der Gelenke prüfen' % int((treffer > 0).sum()))
        np.savez(self.ordner / 'landmarken.npz', roh=roh, treffer=treffer)
        m = None
        if masstab:
            verwendet = [n for n in Engine2d3dKleiderposegelenke.HAUPT if n not in weglassen]
            m = abbildung.masstab(e['k3'], e['cam_t'], e['brennweite'], sam['namen'], verwendet)
        return {'abbildung': abbildung, 'scan': scan, 'alpha': alpha, 'roh': roh, 'treffer': treffer, 'liste': liste, 'masstab': m}
