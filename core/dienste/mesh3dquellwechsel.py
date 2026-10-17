# -*- coding: utf-8 -*-
"""Mesh3dquellwechsel — das Netz (und den Namen) eines Mesh-3D-Auftrags ändern (11.10.2026).

Edgar, mit Bild der Karte „Quelle und Einstellungen“ (nur Text: „Datei: …“, „Figur: Zauberer“): „ich kann nicht mal das Modell ändern!!!“ — Datei und Name gehörten zur Quelle und waren auf der Jobseite nicht änderbar
(`Mesh3dendpunkte.QUELLFELDER`); wer ein anderes Netz wollte, musste einen neuen Auftrag anlegen.

Zwei Fälle:
    nur der Name   Der Stand bekommt den neuen Namen; die Ergebnisse bleiben (das Modell heißt ab dem nächsten Lauf so).
    ein anderes Netz   Datei, Format oder Weg (`Blendimportweg`) ändern sich → die Ergebnisse gehören zur alten Datei und werden verworfen: der Auftrag „Mesh to 3D“ des Imports wird entfernt (sonst bliebe er
                 verwaist in dessen Liste), der Lauf-Zustand im Stand zurückgesetzt (Status „angelegt“ wie nach „Auftrag anlegen“), die Bewegung gelöscht. Was der alte Lauf schrieb (`export/`, `arbeit/`, `ergebnis/`),
                 überschreibt der nächste Lauf; das gespeicherte Modell der alten Datei bleibt und wird mit dem Auftrag gelöscht (`herkunft.import`). Gestartet wird nichts.

Das Format ergibt sich aus der Endung einer gewählten Datei (`.blend`, `.obj`, `.fbx`, `.glb`); ein Ordner behält das Format des Auftrags. Während eines Laufs geht nichts (409 im Endpunkt).
"""

import logging
import shutil
from pathlib import Path

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .blendimportformate import Blendimportformate
from .blendimportloeschen import Blendimportloeschen
from .blendimportquelle import Blendimportquelle
from .blendimportweg import Blendimportweg

logger = logging.getLogger('core')

__all__ = ['Mesh3dquellwechsel']


class Mesh3dquellwechsel:
    class Laeuft(ValueError):
        """Der Auftrag rechnet — der Endpunkt antwortet 409."""

    #: Was ein Lauf an Zustand in den Stand schreibt — ein anderes Netz setzt es zurück.
    LAUFFELDER = ('ergebnis', 'rollen', 'schritt', 'schritte', 'fortschritt', 'detail', 'dauer', 'dauer_s', 'fehler', 'gestartet', 'beendet', 'ab', 'pid', 'aktualisiert')

    def __init__(self, kennung):
        try:
            self.ablage = Blendimportablage(kennung)
        except ValueError as fehler:
            raise ValueError('Kein Auftrag %s' % kennung) from fehler
        self.stand = self.ablage.stand()
        if not self.stand:
            raise ValueError('Kein Auftrag %s' % kennung)

    @staticmethod
    def format_von(pfad, aktuell):
        """Das Format zu einem Pfad: bei einer Datei ihre Endung, bei einem Ordner das bisherige."""
        text = str(pfad or '').strip().strip('"').strip("'").strip()
        datei = Path(text)
        if text and datei.is_file():
            for format, daten in Blendimportformate.FORMATE.items():
                if datei.suffix.lower() == daten['endung']:
                    return format
            raise ValueError('Keine Netzdatei (.blend, .obj, .fbx, .glb): %s' % datei.name)
        return Blendimportformate.pruefen(aktuell)

    def wechseln(self, pfad, eigener_name=''):
        """→ `{quelle, weg, weg_grund, neues_netz, verworfen}`; `ValueError` mit dem Grund (Pfad fehlt, Datei unlesbar, rechnet gerade)."""
        if Blendimportarbeiter.lebt(self.ablage) and self.stand.get('status') in ('laeuft', 'neu'):
            raise self.Laeuft('Der Auftrag rechnet — erst anhalten oder das Ende abwarten')
        alt = self.stand.get('quelle') or {}
        eigener = str(eigener_name or '').strip()
        format = self.format_von(pfad, alt.get('format'))
        quelle = Blendimportquelle(pfad, 'eigen' if eigener else 'ordner', eigener, Blendimportformate.endung(format)).steckbrief()
        try:
            weg, grund = Blendimportweg.erkennen(format, quelle['datei'])
        except (OSError, ValueError) as fehler:
            raise ValueError('Die Datei lässt sich nicht lesen: %s' % fehler) from fehler
        neues_netz = (quelle['datei'], format, weg) != (alt.get('datei'), alt.get('format'), self.stand.get('weg') or Blendimportweg.TEILE)
        verworfen = self._verwerfen() if neues_netz and self.stand.get('ergebnis') else None
        stand = self.ablage.stand()
        if neues_netz:
            for feld in self.LAUFFELDER:
                stand.pop(feld, None)
            stand['status'] = 'neu'
        stand.update(quelle=quelle, weg=weg, weg_grund=grund)
        stand['einstellungen'] = {**(stand.get('einstellungen') or {}), 'pfad': str(pfad).strip(), 'name': 'eigen' if eigener else 'ordner', 'eigener_name': eigener}
        self.ablage.stand_schreiben(stand)
        self.ablage.name_loeschen()                       # der Name kommt jetzt aus der Quelle; ein früher über den Stift gesetzter läge sonst darüber (`Blendimportablage.stand`)
        netz = None
        if neues_netz:
            self._altes_netz_wegraeumen()
            netz = self._neues_netz_ablegen(quelle['datei'], weg)
        return {'quelle': quelle, 'weg': weg, 'weg_grund': grund, 'neues_netz': neues_netz, 'verworfen': verworfen, 'netz': netz}

    #: Was zum Netz der alten Datei gehört und die Mesh-Ansicht der Seite speist: `koerper.glb` samt Ablage daneben, die leichte Vorschau, der Katalog der Inseln des Netz-Werkzeugs.
    #: Edgar, 14.10.2026: „nach Klick auf Quelle übernehmen soll das alte Mesh aus der 2. View weg sein, und das neue geladen werden“ — die Ansicht las weiter `arbeit/koerper.glb` des ALTEN Netzes.
    ALTES_NETZ = ('koerper.glb', 'koerper.glb.scan.npz', 'ansicht', 'netzbearbeitung')

    def _altes_netz_wegraeumen(self):
        for name in self.ALTES_NETZ:
            ziel = self.ablage.arbeit(name)
            if ziel.is_dir():
                shutil.rmtree(ziel, ignore_errors=True)
            else:
                ziel.unlink(missing_ok=True)

    def _neues_netz_ablegen(self, datei, weg):
        """Beim Weg „netz“ das Körpernetz der neuen Datei sofort ablegen (`Blendimportnetz`, ~1 s) — damit steht es in der Mesh-Ansicht, und die leichte Vorschau wird gebaut (`Mesh3dnetzansicht.vorab`), ohne dass ein Lauf nötig ist.
        Beim Weg „teile“ entsteht das Körpernetz erst im Lauf (Blender): die Ansicht bleibt bis dahin leer. Ein Fehler hier ändert nichts am Wechsel (der Lauf legt das Netz selbst ab) → der Bericht, `{'fehler': …}` oder `None`."""
        if weg != Blendimportweg.NETZ:
            return None
        from .blendimportnetz import Blendimportnetz

        try:
            return Blendimportnetz(self.ablage, lambda *argumente: None).schreiben(datei)
        except Exception as fehler:  # noqa: BLE001 — Beiwerk des Wechsels: der Lauf schreibt das Netz ohnehin
            logger.warning('Mesh-3D %s: neues Netz nicht abgelegt', self.ablage.kennung, exc_info=True)
            return {'fehler': str(fehler)}

    def _verwerfen(self):
        """Der Auftrag „Mesh to 3D“ des alten Netzes (Eintrag und Ordner) und die Bewegung auf seiner Figur → die Kennung des entfernten Auftrags oder `None`."""
        auftrag = Blendimportloeschen(self.ablage.kennung)._auftrag_entfernen()  # noqa: SLF001 — dieselbe Entfernung wie beim Löschen des Imports, ohne den Rest davon
        shutil.rmtree(self.ablage.arbeit('bewegung'), ignore_errors=True)
        return auftrag
