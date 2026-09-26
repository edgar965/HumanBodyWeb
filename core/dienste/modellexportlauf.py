# -*- coding: utf-8 -*-
"""Modellexportlauf — die hochgeladenen Exportdateien ablegen, `.blend` bauen.

DER BROWSER SCHREIBT DIE FORMATE, NICHT DIESE KLASSE (26.09.2026,
Docu/konzept_modellexport.md)
==================================================================
GLB, OBJ+MTL, PLY, STL und DAE entstehen vollständig im Viewer (Three.js-
Exporter bzw. der eigene Collada-Schreiber) — hier kommt nur die Ablage der
fertigen Bytes. Einzige Ausnahme: `.blend` ist Blenders eigenes Format, dafür
läuft Blender im Hintergrund (`modellexportblend.py`, GLB -> .blend).

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

    def __init__(self, ordner_roh, name_roh, dateien, blend_quelle=None):
        self.ordner_roh = ordner_roh
        self.name_roh = name_roh
        self.dateien = dateien  # Liste von UploadedFile, Namen mit PLATZHALTER
        self.blend_quelle = blend_quelle  # UploadedFile oder None

    def ausfuehren(self):
        """Wirft `ZielAbgelehnt` — sonst `{ordner, dateien: [{name, bytes}]}`."""
        ordner = Modellexportziel.ordner(self.ordner_roh)
        stamm = Modellexportziel.name(self.name_roh)
        endungen = {self._endung(f.name) for f in self.dateien}
        if self.blend_quelle is not None:
            endungen.add('.blend')
        stamm = Modellexportziel.eindeutiger_stamm(ordner, stamm, endungen)

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
            geschrieben.append(self._blend_bauen(ordner, stamm))

        return {'ordner': str(ordner), 'dateien': geschrieben}

    # --------------------------------------------------------------- Ablegen

    @staticmethod
    def _endung(dateiname):
        idx = dateiname.rfind('.')
        return dateiname[idx:].lower() if idx >= 0 else ''

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

    def _blend_bauen(self, ordner, stamm):
        """GLB nach ProjektTemp, Blender darüber, Ergebnis in `ordner`."""
        glb_temp = ProjektTemp.datei(suffix='.glb', prefix='modellexport_')
        blend_pfad = ordner / ('%s.blend' % stamm)
        try:
            self._schreiben(self.blend_quelle, glb_temp)
            befehl = [
                # --factory-startup: ohne Edgars Add-ons (KeenTools, MPFB,
                # HumanBodyBlender, …) starten — eines davon legte sonst ein
                # eigenes Boilerplate-Objekt in der Export-Szene an, siehe
                # `modellexportblend.py`-Docstring (Fund 26.09.2026).
                str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python',
                str(settings.MODELLEXPORT_BLENDER_SKRIPT), '--',
                '--glb', str(glb_temp), '--blend', str(blend_pfad),
            ]
            ergebnis = subprocess.run(
                befehl, capture_output=True, text=True, timeout=BLENDER_TIMEOUT_S,
            )
            if ergebnis.returncode != 0 or not blend_pfad.is_file():
                logger.error('Modellexportlauf: Blender fehlgeschlagen (%d): %s',
                             ergebnis.returncode, ergebnis.stderr[-2000:])
                raise ZielAbgelehnt('Blender konnte keine .blend schreiben (siehe Log)')
        except subprocess.TimeoutExpired:
            logger.error('Modellexportlauf: Blender lief in den Zeitlimit (%ds)', BLENDER_TIMEOUT_S)
            raise ZielAbgelehnt('Blender hat das Zeitlimit überschritten (%ds)' % BLENDER_TIMEOUT_S) from None
        finally:
            ProjektTemp.weg(glb_temp)
        return {'name': blend_pfad.name, 'bytes': blend_pfad.stat().st_size}
