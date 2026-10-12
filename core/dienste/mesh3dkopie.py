# -*- coding: utf-8 -*-
"""Mesh3dkopie — einen Mesh-3D-Auftrag kopieren, ohne oder mit allen Daten (11.10.2026).

Edgar: „die Jobs sind ja echte Kacke, die Kopie-Möglichkeit für Jobs vergessen“. Wie bei „2D3D Kleider“ zwei Wege (`Engine2d3dKleiderauftragskopie`, `Auftragsduplikat`):

    ohne Daten   Eingabe und Einstellungen — dieselbe Datei, dieselbe Grundfigur, dieselben Optionen; ein neuer Auftrag im Zustand „angelegt“, nichts gerechnet
    mit Daten    der ganze Importordner (Export, Arbeit, Ergebnis, Stand, Log) samt EIGENEM Auftrag „Mesh to 3D“ (`Mesh3dkopiefigur`); die Kopie steht im selben Schritt wie die Quelle

Der Name ist ein Teil des Imports (er wird Name des gespeicherten Modells und Dateiname der Stücke, `Blendimportquelle.NAME_MAX`, keine Sonderzeichen): „Zauberer“ → „Zauberer Kopie“,
„Zauberer Kopie 2“ … — nie derselbe wie ein vorhandener, sonst überschriebe der Lauf der Kopie das Modell der Quelle. NICHT kopiert: das gespeicherte Modell (`ergebnis.modell`, es gehört der
Quelle; „Neu berechnen“ ab „Modell“ schreibt eines unter dem neuen Namen), Stücke der Garderobe (sie tragen den alten Namen; der Lauf der Kopie schreibt eigene) und alles außerhalb des Importordners.
Eine Quelle, die rechnet, wird nicht kopiert; die Kopie startet nichts.
"""

import itertools
import logging
import re
from pathlib import Path

from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .blendimportquelle import Blendimportquelle
from .mesh3dkopiefigur import Mesh3dkopiefigur
from .ordnerkopie import Ordnerkopie

logger = logging.getLogger('core')

__all__ = ['Mesh3dkopie']


class Mesh3dkopie:
    WORT = 'Kopie'
    _ENDE = re.compile(r'\s+Kopie(?:\s+\d+)?$')

    def __init__(self, kennung):
        try:
            self.quelle = Blendimportablage(kennung)
        except ValueError as fehler:
            raise ValueError('Kein Auftrag %s' % kennung) from fehler
        self.stand = self.quelle.stand()
        if not self.stand:
            raise ValueError('Kein Auftrag %s' % kennung)
        self.name = (self.stand.get('quelle') or {}).get('name') or self.quelle.kennung

    # ------------------------------------------------------------------ Prüfen und Benennen

    def pruefen(self):
        if Blendimportarbeiter.lebt(self.quelle) and self.stand.get('status') in ('laeuft', 'neu'):
            raise ValueError('„%s“ rechnet gerade — erst abwarten oder anhalten' % self.name)

    @staticmethod
    def namen():
        """Die Namen aller vorhandenen Aufträge, klein geschrieben."""
        return {((Blendimportablage(k).stand().get('quelle') or {}).get('name') or '').lower() for k in Blendimportablage.alle()}

    def neuer_name(self):
        """„Zauberer“ → „Zauberer Kopie“, dann „Zauberer Kopie 2“ …: der erste, den es noch nicht gibt (höchstens `NAME_MAX` Zeichen)."""
        basis = self._ENDE.sub('', self.name).strip() or self.name
        belegt = self.namen()
        for nummer in itertools.count(1):
            ende = ' %s' % self.WORT if nummer == 1 else ' %s %d' % (self.WORT, nummer)
            kandidat = basis[:Blendimportquelle.NAME_MAX - len(ende)].rstrip() + ende
            if kandidat.lower() not in belegt:
                return kandidat

    @staticmethod
    def _neue_kennung():
        return Auftragskennung.frei(timezone.now(), lambda k: Blendimportablage(k).ordner().exists())

    def _einstellungen(self, name):
        """Die Einstellungen der Quelle mit dem NEUEN Namen als eigenem Namen: das Feld „Name der Figur“ der Jobseite zeigt ihn, und „Quelle übernehmen“ schreibt ihn nicht auf den des Originals zurück."""
        return {**(self.stand.get('einstellungen') or {}), 'name': 'eigen', 'eigener_name': name}

    def _kopie(self, umfang):
        return {'von': self.quelle.kennung, 'name': self.name, 'am': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'), 'umfang': umfang}

    # ------------------------------------------------------------------ Ohne Daten

    def ohne_daten(self):
        """Ein neuer Auftrag mit derselben Datei und denselben Einstellungen, nichts gerechnet → seine Kennung."""
        self.pruefen()
        quelle = dict(self.stand.get('quelle') or {})
        if not quelle.get('datei') or not Path(quelle['datei']).exists():
            raise ValueError('Die Datei von „%s“ gibt es nicht mehr: %s' % (self.name, quelle.get('datei')))
        kennung, name = self._neue_kennung(), self.neuer_name()
        ablage = Blendimportablage(kennung)
        ablage.anlegen()
        ablage.stand_schreiben({
            'kennung': kennung, 'status': 'neu', 'bereich': self.stand.get('bereich') or 'mesh3d', 'quelle': {**quelle, 'name': name},
            'einstellungen': self._einstellungen(name), 'weg': self.stand.get('weg') or 'teile',
            'weg_grund': self.stand.get('weg_grund') or '', 'angelegt': timezone.now().isoformat(), 'kopie': self._kopie('ohne Daten')})
        logger.info('Kopie Mesh-3D ohne Daten: %s (%s) → %s (%s)', self.name, self.quelle.kennung, name, kennung)
        return kennung

    # ------------------------------------------------------------------ Mit Daten

    def mit_daten(self):
        """Ordner und Auftrag „Mesh to 3D“ kopieren, der Stand bleibt wie in der Quelle → die Kennung der Kopie. Ohne Ergebnis (nichts gerechnet) ist es die Kopie ohne Daten."""
        self.pruefen()
        if not self.stand.get('ergebnis'):
            return self.ohne_daten()
        kennung, name = self._neue_kennung(), self.neuer_name()
        ziel = Blendimportablage(kennung)
        figur = self._figur(name)
        ersetzungen = {self.quelle.kennung: kennung}
        if figur is not None:
            ersetzungen.update(figur.ersetzungen)
        ordner = Ordnerkopie(self.quelle.ordner(), ziel.ordner(), ersetzungen)
        neu = None
        try:
            zahl, groesse = ordner.kopieren()
            neu = figur.kopieren() if figur is not None else None
            ziel.stand_schreiben(self._stand(kennung, name, ersetzungen, ordner, neu))
        except BaseException:
            ordner.entfernen()
            if neu is not None:
                figur.zuruecknehmen(neu)
            raise
        logger.info('Kopie Mesh-3D mit Daten: %s (%s) → %s (%s), %d Dateien, %.1f MB', self.name, self.quelle.kennung, name, kennung, zahl, groesse / 1e6)
        return kennung

    def _figur(self, name):
        """Die Kopie des Auftrags „Mesh to 3D“ (noch nicht angelegt) oder `None`, wenn die Quelle keinen hat."""
        from ..models import Meshfigurauftrag

        figur_id = ((self.stand.get('ergebnis') or {}).get('figur') or {}).get('id')
        try:
            job = Meshfigurauftrag.objects.filter(pk=figur_id).first() if figur_id else None
        except (ValueError, TypeError):
            job = None
        if job is None:
            return None
        return Mesh3dkopiefigur(job, name if job.name == self.name else '%s %s' % (job.name, self.WORT))

    def _stand(self, kennung, name, ersetzungen, ordner, figur):
        """`stand.json` der Kopie: der Text der Quelle mit den neuen Kennungen, dann Name, Herkunft, ohne PID und ohne das gespeicherte Modell."""
        import json

        stand = json.loads(ordner.ersetzen(json.dumps(self.stand, ensure_ascii=False)))
        stand.update(kennung=kennung, kopie=self._kopie('alles'))
        stand['quelle']['name'] = name
        stand['einstellungen'] = self._einstellungen(name)
        stand.pop('pid', None)
        ergebnis = stand.get('ergebnis') or {}
        ergebnis.pop('modell', None)
        if figur is not None:
            ergebnis['figur'] = {**(ergebnis.get('figur') or {}), 'id': str(figur.id), 'kennung': figur.kennung}
        return stand
