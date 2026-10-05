# -*- coding: utf-8 -*-
"""Engine2d3dKleidersegmentierung — Schritt „segmentierung" von „2D3D Kleider": die Fotos in Körperteile und Kleidung zerlegen (04.10.2026).

Edgar (04.10.2026): „baue das ein in den 2d3dKleider jobs — optional nach der Mesh erzeugung". Der Schritt steht nach dem Netz (er braucht dessen Flächen) und vor dem Körper (dessen Schritt
„kleidung" die Etiketten sonst nicht mehr sähe). Er ist OPTIONAL: Im vollen Lauf läuft er nur bei `segmentierung.verwenden = an`; ausdrücklich gestartet („Segmentierung starten", „ab Segmentierung")
läuft er immer, dann sind die Überlagerungen das Ergebnis und die Kleidung hängt noch nicht davon ab (`Engine2d3dKleidersegmentierungsoptionen`).

Die Rechnung steht in `VideoToBVH/wrappers/_run_sapiens.py` (Umgebung `settings.PIPELINE_PYTHON`, `python10`): Sapiens-Körperteil-Modell auf den vorbereiteten Fotos (`vorbereitet/<stamm>.png`), Überlagerungen
nach `segmentierung/`, Flächenstimmen nach `arbeit/sapiens_flaechen.npz`. Hier nur: Auftragsbeschreibung schreiben, Zeilen des Runners deuten, Fortschritt und Ergebnis in den Auftrag
(`job.ergebnis['segmentierung']`). Die Stimmen nutzt `Meshfigurkleidung._sapiens` (Schritt „kleidung" der Körper-Kette, Quelle „rechnen").

Zeilen des Runners (stdout): `[fortschritt] <0..99> <Text>`, `[bild] {…}`, `[ergebnis] {…}`.
"""

import json
import logging
import os

from django.conf import settings

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..daten.wrapperpfad import Wrapperpfad
from ..pipeline_process import PipelineProzess, PipelineStille
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleidernetz import Engine2d3dKleidernetz
from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidersegmentierung']


class Engine2d3dKleidersegmentierung:
    RUNNER = '_run_sapiens.py'
    #: So lange darf der Runner schweigen — die Gewichte laden meldet alle 2 %, das Modell laden dauert Sekunden.
    STILLE_S = 1800
    #: Die Rollen, die eine Ansicht des Netzes sind (`mesh_fototextur.ACHSEN`); „gesicht" und „aus" gehören nicht dazu.
    ROLLEN = ('vorne', 'hinten', 'links', 'rechts')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Engine2d3dKleideroptionen.segmentierung(self.job.optionen)
        self._ergebnis = None

    def gebraucht(self):
        """Braucht der volle Lauf die Etiketten? Für die Kleidungsmaske (`verwenden = an`) oder für die Haarmaske (`haar` Sapiens oder beides)."""
        return self.optionen.get('verwenden') == 'an' or self.optionen.get('haar') in ('sapiens', 'beide')

    def ausfuehren(self):
        if not self.gebraucht() and getattr(self.lauf, 'ab', None) != 'segmentierung':
            logger.info('2D3D Kleider %s: Segmentierung aus (Option) — übersprungen', self.job.kennung)
            self.lauf.melden(1.0, 'Segmentierung aus (Option) — übersprungen')
            return
        auftrag = self.ablage.segmentierung('auftrag.json')
        auftrag.parent.mkdir(parents=True, exist_ok=True)
        auftrag.write_text(json.dumps(self.beschreibung(), ensure_ascii=False, indent=1), encoding='utf-8')
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        pp = PipelineProzess.starten([settings.PIPELINE_PYTHON, runner, str(auftrag)], cwd=Wrapperpfad.pfad(), env_extra=self.umgebung())
        logger.info('2D3D Kleider %s: Segmentierungs-Runner %s gestartet', self.job.kennung, pp.proc.pid)
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                self._zeile(zeile.rstrip('\n'))
                if self.lauf.angehalten():
                    pp.beenden()
                    raise self.lauf.Angehalten()
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('Segmentierungs-Runner schweigt (%s)' % fehler) from fehler
        rc = pp.warten(timeout=120)
        if rc != 0 or self._ergebnis is None:
            raise RuntimeError('Segmentierungs-Runner endete mit %s: %s' % (rc, pp.fehlertext(1500) or 'ohne Meldung'))
        self._abschluss()

    # ------------------------------------------------------------- Auftrag

    def beschreibung(self):
        """Was der Runner rechnen soll: das Netz, die vorbereiteten Fotos mit Rolle, die Ordner (JSON `segmentierung/auftrag.json`)."""
        netz = self.ablage.netzdatei(original=True)             # nie das Tiefennetz: der Stand der Stimmen merkt sich Größe und Änderungszeit dieser Datei
        if netz is None:
            raise RuntimeError('Kein Netz — erst der Schritt „netz"')
        bilder = self.bilder_fuer(self.job, self.ablage)
        if not bilder:
            raise RuntimeError('Keine vorbereiteten Fotos mit Rolle vorne/hinten/links/rechts — erst „Vorbereitung" oder „Netz"')
        return {
            'kennung': self.job.kennung,
            'netz': str(netz),
            'bilder': bilder,
            'hf_home': str(settings.HF_HOME_DIR),
            'ordner': {'segmentierung': str(self.ablage.segmentierung()), 'arbeit': str(self.ablage.arbeit())},
            # Die Einstellungen, die ändern, WAS Sapiens rechnet (Modellgröße, Flächenbild, Fotokante, Rand) — der Runner legt sie im Stand ab, damit „veraltet" sie erkennt.
            'optionen': Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(self.optionen),
        }

    @classmethod
    def bilder_fuer(cls, job, ablage):
        """Die Fotos, die eine Ansicht des Netzes sind: `[{datei, stamm, rolle, png}]` — nur mit vorbereitetem PNG und einer Rolle aus `ROLLEN`. Die Rolle ist die gestellte, bei „Automatisch"
        die vom Vorbereitungsschritt erkannte (`vorbereitet/vorbereitung.json`), sonst die im Netzschritt erkannte (`job.bilder[].erkannt`). Auch die Seite fragt es (`…segmentierungsliste`)."""
        ordner = ablage.unter(Engine2d3dKleiderablage.VORBEREITET)
        try:
            stand = json.loads((ordner / 'vorbereitung.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            stand = {}
        aus_stand = {e.get('datei'): e.get('rolle') for e in stand.get('bilder', []) if isinstance(e, dict)}
        erkannt = {b.get('datei'): b.get('erkannt') for b in (job.bilder or []) if isinstance(b, dict)}
        aus = []
        for eintrag in Engine2d3dKleidernetz.bilder_fuer(job, ablage):
            datei = eintrag['datei']
            rolle = next((r for r in (eintrag['rolle'], aus_stand.get(datei), erkannt.get(datei)) if r in cls.ROLLEN), None)
            stamm = os.path.splitext(datei)[0]
            png = ordner / (stamm + '.png')
            if rolle is not None and png.is_file():
                aus.append({'datei': datei, 'stamm': stamm, 'rolle': rolle, 'png': str(png)})
        return aus

    def umgebung(self):
        """Gewichte unter `hf_home`, Zwischendateien im Auftrag (nie System-Temp)."""
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        return {'HF_HOME': str(settings.HF_HOME_DIR), 'PYTORCH_CUDA_ALLOC_CONF': 'expandable_segments:True', 'TMP': str(tmp), 'TEMP': str(tmp)}

    # --------------------------------------------------------------- Zeilen

    def _zeile(self, zeile):
        if zeile.startswith('[fortschritt] '):
            teile = zeile[len('[fortschritt] '):].split(' ', 1)
            try:
                wert = max(0, min(99, int(float(teile[0]))))
            except ValueError:
                return
            self.lauf.melden(wert / 100.0, teile[1] if len(teile) > 1 else '')
        elif zeile.startswith('[ergebnis] '):
            try:
                self._ergebnis = json.loads(zeile[len('[ergebnis] '):])
            except ValueError:
                logger.error('2D3D Kleider %s: Ergebniszeile der Segmentierung nicht lesbar: %.200s', self.job.kennung, zeile)

    def _abschluss(self):
        job = self.job
        job.ergebnis = {**(job.ergebnis or {}), 'segmentierung': dict(self._ergebnis, verwenden=self.optionen.get('verwenden'))}
        self.lauf.sichern('ergebnis')
        kennzahlen = self._ergebnis.get('kennzahlen') or {}
        logger.info('2D3D Kleider %s: Segmentierung fertig (%s Fotos, %s von %s Flächen gesehen)', job.kennung, self._ergebnis.get('bilder'),
                    kennzahlen.get('flaechen_gesehen'), kennzahlen.get('flaechen_gesamt'))
