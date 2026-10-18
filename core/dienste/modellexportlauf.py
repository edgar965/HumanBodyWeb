# -*- coding: utf-8 -*-
"""Modellexportlauf — die hochgeladenen Exportdateien ablegen, `.blend` bauen.

DER BROWSER SCHREIBT DIE FORMATE, NICHT DIESE KLASSE (26.09.2026,
Docu/konzept_modellexport.md)
==================================================================
GLB, OBJ+MTL, PLY, STL, DAE und die vier JPG-Ansichten entstehen vollständig
im Viewer (Three.js-Exporter, der eigene Collada-Schreiber, `Modellansichten`)
— hier kommt nur die Ablage der fertigen Bytes. Einzige Ausnahme: `.blend` und
`.fbx` (seit 18.10.2026) schreibt Blender im Hintergrund aus der GLB, beide in
EINEM Lauf (`modellexportblend.py`).

PLATZHALTER STATT ZWEITEM FELD
===============================
Jede hochgeladene Datei heißt clientseitig `MODELL<Rest>` (`MODELL.glb`,
`MODELL.mtl`, `MODELL_Haut.png`, …) — `PLATZHALTER` unten. Der Server ersetzt
das Präfix durch den geprüften, eindeutigen Stamm. So teilen sich alle Dateien
EINES Exports denselben Stamm, ohne dass Client und Server ihn zweimal
aushandeln müssen.
"""

import logging
import subprocess

from django.conf import settings

from ..projekt_temp import ProjektTemp
from .modellexportziel import Modellexportziel, ZielAbgelehnt

logger = logging.getLogger('core')

__all__ = ['Modellexportlauf', 'ZielAbgelehnt']

#: Siehe Moduldocstring — muss mit `static/viewer/scene/modellexport.js`
#: übereinstimmen (dort als `Modellexport.PLATZHALTER`).
PLATZHALTER = 'MODELL'

#: Blender braucht bei Genesis-9-Texturen mehr als eine Minute; 180 s liegen
#: darüber, ohne eine hängende Anfrage endlos offen zu lassen.
BLENDER_TIMEOUT_S = 180

#: Diese Textformate verweisen per TEXT-Inhalt aufeinander (`.obj` -> `mtllib
#: MODELL.mtl`, `.mtl` -> `map_Kd MODELL_mat_0.png`, `.dae` -> `<init_from>`
#: mit PNG-Namen) — beim Umbenennen muss der PLATZHALTER dort genauso ersetzt
#: werden wie im Dateinamen, sonst zeigen die Referenzen ins Leere (gefunden
#: 26.09.2026: MeshLab meldete beim Öffnen einer exportierten .obj „textures
#: have not been loaded", weil die .mtl noch `MODELL_mat_0.png` verwies).
TEXTFORMATE = {'.obj', '.mtl', '.dae'}


class Modellexportlauf:
    """Ein Exportauftrag: Ziel prüfen, Dateien ablegen, .blend bauen."""

    def __init__(self, ordner_roh, name_roh, dateien, blend_quelle=None, fps=30, polygone=1.0,
                 direkt=False, blender_formate=('blend',)):
        self.ordner_roh = ordner_roh
        self.name_roh = name_roh
        self.dateien = dateien  # Liste von UploadedFile, Namen mit PLATZHALTER
        self.blend_quelle = blend_quelle  # UploadedFile (GLB) oder None
        self.fps = fps  # Szenen-FPS der .blend — die GLB ist schon in dieser Rate abgetastet
        self.polygone = polygone  # Anteil der Dreiecke im .blend-/.fbx-Export (1 = Original)
        # True: genau in DEN Ordner, gleichnamige Dateien werden überschrieben (Dialog der Szene seit
        # 18.10.2026 — der Ordner trägt dort schon den Modellnamen, der Dialog meldet Vorhandenes vorher).
        self.direkt = direkt
        # Was Blender aus `blend_quelle` macht: 'blend' und/oder 'fbx' (FBX seit 18.10.2026).
        self.blender_formate = tuple(blender_formate) or ('blend',)

    def ausfuehren(self):
        """Wirft `ZielAbgelehnt` — sonst `{ordner, dateien: [{name, bytes}]}`."""
        ordner = Modellexportziel.ordner(self.ordner_roh)
        stamm = Modellexportziel.name(self.name_roh)
        # Ein Export = ein Unterordner (Edgar, 26.09.2026): eine `.obj` bringt
        # `.mtl` und ein PNG JE MATERIALZONE mit — bei Genesis 9 sind das
        # siebzehn Bilder, die sonst mit denen jedes anderen Exports im selben
        # Verzeichnis liegen. Alles beieinander heißt zugleich, dass die
        # relativen Verweise (`mtllib`, `map_Kd`) weiter stimmen.
        if not self.direkt:
            ordner = self._freie_ablage(ordner, stamm)
            stamm = ordner.name

        geschrieben = []
        for datei in self.dateien:
            zielname = self._umbenannt(datei.name, stamm)
            pfad = ordner / zielname
            if self._endung(zielname) in TEXTFORMATE:
                self._schreiben_text(datei, pfad, stamm)
            else:
                self._schreiben(datei, pfad)
            geschrieben.append({'name': zielname, 'bytes': pfad.stat().st_size})

        if self.blend_quelle is not None:
            geschrieben.extend(self._blender_bauen(ordner, stamm))

        return {'ordner': str(ordner), 'dateien': geschrieben}

    @staticmethod
    def vorhanden(ordner, stamm, endungen):
        """Welche `<stamm><endung>` in `ordner` schon liegen — die ein direkter Export überschriebe."""
        return [stamm + e for e in endungen if (ordner / (stamm + e)).is_file()]

    # --------------------------------------------------------------- Ablegen

    @staticmethod
    def _endung(dateiname):
        idx = dateiname.rfind('.')
        return dateiname[idx:].lower() if idx >= 0 else ''

    @staticmethod
    def _freie_ablage(ordner, stamm):
        """Ein noch nicht belegter Unterordner `<ordner>/<stamm>`, angelegt.

        Der Ordnername IST der Namensstamm der Dateien darin — ein zweiter
        Export unter demselben Namen wird zu `<stamm>_2`, nicht zu einem
        Mischmasch im selben Verzeichnis.
        """
        for versuch in range(1, 1000):
            ziel = ordner / (stamm if versuch == 1 else '%s_%d' % (stamm, versuch))
            if not ziel.exists():
                ziel.mkdir(parents=True)
                return ziel
        raise ZielAbgelehnt('Kein freier Unterordner für „%s"' % stamm)

    @staticmethod
    def _umbenannt(dateiname, stamm):
        """`MODELL_Haut.png` -> `<stamm>_Haut.png`. Kein Präfix, keine Ablage."""
        if not dateiname.startswith(PLATZHALTER):
            raise ZielAbgelehnt('Unerwarteter Dateiname: %s' % dateiname)
        return stamm + dateiname[len(PLATZHALTER):]

    @staticmethod
    def _schreiben(datei, pfad):
        with open(pfad, 'wb') as ziel:
            for stueck in datei.chunks():
                ziel.write(stueck)

    @staticmethod
    def _schreiben_text(datei, pfad, stamm):
        """Wie `_schreiben`, ersetzt zusätzlich den PLATZHALTER im Text —
        die Datei referenziert damit die (ebenfalls umbenannten) Nachbardateien
        korrekt, statt auf `MODELL…`-Namen zu zeigen, die es nicht mehr gibt."""
        text = b''.join(datei.chunks()).decode('utf-8')
        text = text.replace(PLATZHALTER, stamm)
        with open(pfad, 'w', encoding='utf-8') as ziel:
            ziel.write(text)

    # ----------------------------------------------------------------- Blend

    def _blender_bauen(self, ordner, stamm):
        """GLB nach ProjektTemp, EIN Blender-Lauf für alle `blender_formate`, Ergebnisse in `ordner`."""
        glb_temp = ProjektTemp.datei(suffix='.glb', prefix='modellexport_')
        ziele = {f: ordner / ('%s.%s' % (stamm, f)) for f in self.blender_formate}
        try:
            self._schreiben(self.blend_quelle, glb_temp)
            befehl = [
                # --factory-startup: ohne Edgars Add-ons (KeenTools, MPFB,
                # HumanBodyBlender, …) starten — eines davon legte sonst ein
                # eigenes Boilerplate-Objekt in der Export-Szene an, siehe
                # `modellexportblend.py`-Docstring (Fund 26.09.2026).
                str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python',
                str(settings.MODELLEXPORT_BLENDER_SKRIPT), '--',
                '--glb', str(glb_temp), '--fps', str(self.fps), '--polygone', str(self.polygone),
            ]
            for format_, pfad in ziele.items():
                befehl += ['--%s' % format_, str(pfad)]
            ergebnis = subprocess.run(
                befehl, capture_output=True, text=True, timeout=BLENDER_TIMEOUT_S,
            )
            fehlt = [p.name for p in ziele.values() if not p.is_file()]
            if ergebnis.returncode != 0 or fehlt:
                logger.error('Modellexportlauf: Blender fehlgeschlagen (%d, fehlt %s): %s',
                             ergebnis.returncode, fehlt, ergebnis.stderr[-2000:])
                raise ZielAbgelehnt('Blender konnte %s nicht schreiben (siehe Log)'
                                    % ', '.join(fehlt or ziele))
        except subprocess.TimeoutExpired:
            logger.error('Modellexportlauf: Blender lief in den Zeitlimit (%ds)', BLENDER_TIMEOUT_S)
            raise ZielAbgelehnt('Blender hat das Zeitlimit überschritten (%ds)' % BLENDER_TIMEOUT_S) from None
        finally:
            ProjektTemp.weg(glb_temp)
        return [{'name': p.name, 'bytes': p.stat().st_size} for p in ziele.values()]
