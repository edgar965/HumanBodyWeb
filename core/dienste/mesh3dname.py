# -*- coding: utf-8 -*-
"""Mesh3dname — den Namen eines Mesh-3D-Auftrags auf der Jobseite ändern (12.10.2026).

Edgar: „Name des Jobs nicht änderbar (schau die 2D3D Kleider an, da ist der Name änderbar)“. Dort ist die Überschrift selbst das Eingabefeld (`gemeinsam/auftragname.js`, Klick oder Stift, Enter speichert);
bei Mesh-3D stand der Name nur in der Karte „Quelle“ und änderte sich dort zusammen mit der Datei (`Mesh3dquellwechsel`).

Der Name eines Auftrags ist `stand.quelle.name`. Die Liste, die Überschrift, der Tab-Titel und die Kopie lesen ihn dort; die Karte „Quelle“ zeigt `einstellungen.eigener_name`. Beides wird gesetzt, damit die Karte nach dem
Umbenennen denselben Namen zeigt und ein späteres „Netz ändern“ ihn behält. Es gilt die Regel des Import-Namensfelds (`Blendimportquelle.eigener`: Buchstaben, Ziffern, Leerzeichen, Bindestrich, höchstens 60 Zeichen),
weil der Name Teil von Dateinamen der Stücke wird.

**Auftrag „Mesh to 3D“ und gespeichertes Modell ziehen mit** (12.10.2026, Edgar: „dann fixe das!“ — die Liste zeigte „Zauberer S0“, die Spalte Modell weiter „Zauberer S0 ohne Zug Mesh“): `angleichen` setzt `Meshfigurauftrag.name` auf den neuen Namen und benennt
das Modell um (`Modellablage.umbenennen`: Datei, Fotokacheln und ihre Adressen; die Szene `.scene.json` bleibt, wie bei jedem Umbenennen). Der neue Modellname ist der alte, bei dem der Name des Auftrags „Mesh to 3D“ am Anfang durch den neuen ersetzt ist
(`Zauberer S0 ohne Zug Mesh` → `Zauberer S0 Mesh`; ein Zähler wie „ 2“ bleibt). Fängt der Modellname nicht mit dem alten Auftragsnamen an (von Hand gespeichert) oder gibt es den neuen Namen schon, bleibt das Modell, wie es ist — der Grund steht im Bericht.
Ausgelagerte Ordner mit dem alten Namen (`output/Export/MeshTo3D/<Name>_<Zeit>`) werden nicht umgezogen, sie sind Ablage des Laufs.
Während eines Laufs geht nichts: der Arbeitsprozess schreibt `stand.json` aus seinem Speicher und würde den neuen Namen zurücksetzen (409 im Endpunkt, wie bei `Mesh3dquellwechsel`).
"""

import logging

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .blendimportquelle import Blendimportquelle
from .umaablage import Ablagefehler

logger = logging.getLogger(__name__)

__all__ = ['Mesh3dname']


class Mesh3dname:
    class Laeuft(ValueError):
        """Der Auftrag rechnet — der Endpunkt antwortet 409."""

    def __init__(self, kennung):
        try:
            self.ablage = Blendimportablage(kennung)
        except ValueError as fehler:
            raise ValueError('Kein Auftrag %s' % kennung) from fehler
        self.stand = self.ablage.stand()
        if not self.stand:
            raise ValueError('Kein Auftrag %s' % kennung)

    def setzen(self, text):
        """→ der gespeicherte Name; `ValueError` bei leerem Text, `Laeuft`, solange der Auftrag rechnet."""
        name = Blendimportquelle.eigener(text)
        if Blendimportarbeiter.lebt(self.ablage) and self.stand.get('status') in ('laeuft', 'neu'):
            raise self.Laeuft('Der Auftrag rechnet — den Namen nach dem Lauf ändern (oder erst anhalten)')
        stand = self.ablage.stand()
        stand['quelle'] = {**(stand.get('quelle') or {}), 'name': name}
        stand['einstellungen'] = {**(stand.get('einstellungen') or {}), 'name': 'eigen', 'eigener_name': name}
        self.ablage.stand_schreiben(stand)
        self.angeglichen = self.angleichen()
        return name

    def angleichen(self):
        """Den Auftrag „Mesh to 3D“ und das gespeicherte Modell auf den Namen dieses Auftrags ziehen. → `{'figur': Text, 'modell': Text}`; wirft nie (ein Fehler hier darf das Umbenennen nicht rückgängig machen)."""
        try:
            return self._angleichen()
        except Exception as fehler:  # noqa: BLE001
            logger.exception('Mesh-3D %s: Auftrag/Modell nicht angeglichen', self.ablage.kennung)
            return {'figur': 'Fehler: %s' % fehler, 'modell': 'bleibt'}

    def _angleichen(self):
        from ..models import Meshfigurauftrag
        from .modellablage import Modellablage

        stand = self.ablage.stand()
        name = (stand.get('quelle') or {}).get('name')
        kennung = ((stand.get('ergebnis') or {}).get('figur') or {}).get('kennung')
        job = Meshfigurauftrag.objects.filter(kennung=kennung).first() if kennung else None
        if not name or job is None:
            return {'figur': 'kein Auftrag „Mesh to 3D“', 'modell': 'bleibt'}
        if job.status == 'laeuft':
            return {'figur': 'rechnet gerade', 'modell': 'bleibt'}
        alt, modell = job.name, job.modell
        bericht = {'figur': 'gleich', 'modell': 'bleibt'}
        if alt != name:
            job.name = name
            job.save(update_fields=['name', 'updated_at'])
            bericht['figur'] = 'umbenannt'
        if not modell or not alt or not modell.startswith(alt) or alt == name:
            bericht['modell'] = 'bleibt (Name beginnt nicht mit dem alten Auftragsnamen)' if modell and alt != name else bericht['modell']
            return bericht
        neu = name + modell[len(alt):]
        try:
            Modellablage.umbenennen(modell, neu)
        except Ablagefehler as fehler:
            bericht['modell'] = 'bleibt (%s)' % fehler
            return bericht
        job.modell = neu
        job.save(update_fields=['modell', 'updated_at'])
        stand = self.ablage.stand()
        eintrag = (stand.get('ergebnis') or {}).get('modell')
        if isinstance(eintrag, dict) and eintrag.get('name') == modell:
            eintrag['name'] = neu
            self.ablage.stand_schreiben(stand)
        bericht['modell'] = 'umbenannt: %s → %s' % (modell, neu)
        logger.info('Mesh-3D %s: Modell %s', self.ablage.kennung, bericht['modell'])
        return bericht
