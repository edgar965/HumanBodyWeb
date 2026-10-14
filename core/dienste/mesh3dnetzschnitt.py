# -*- coding: utf-8 -*-
"""Mesh3dnetzschnitt — Flächen aus dem Netz eines Mesh-3D-Auftrags herausnehmen und als neue Datei speichern (13.10.2026, „Netz bearbeiten“).

Edgar: „… ausschneiden, das Mesh speichern, und dann das 3D Modell neu rechnen“. Der Browser schickt `schnitte` — eine Liste von Auswahlen (`Mesh3dnetzauswahl`), jede eine Liste von Schritten; die Flächen aller
Schnitte werden entfernt. Die Auswahlen beziehen sich immer auf das ORIGINAL (nicht auf das, was ein früherer Schnitt übrig ließ): die Flächennummern ändern sich beim Entfernen nicht, die Reihenfolge der Schnitte
spielt keine Rolle.

Geschnitten wird die QUELLDATEI des Auftrags (`stand.quelle.datei`, eine GLB mit einem Netz), nicht `koerper.glb`: beide haben dieselben Flächen in derselben Reihenfolge (`koerper.glb` ist die Quelle mit einer
Skalierung am Wurzelknoten, `Blendimportnetz`), und die neue Datei soll wieder Quelle werden. Entfernt werden die Flächen und danach alle Punkte, die nirgends mehr gebraucht werden; Material, UV und Textur bleiben.
Das Original wird nie überschrieben: die neue Datei liegt in `3DObjects/mesh3d_eingang/<Kennung>/<Name>/<Name>_bearbeitet_<Zeit>.glb`, daneben eine `.json` mit Quelle, Schnitten und Zahlen (wie die Datei
entstand, und wiederholbar auf einem anderen Original). Nach dem Schreiben wird sie neu gelesen und die Flächenzahl gegengeprüft; stimmt sie nicht, wird sie wieder gelöscht.

„Als Quelle übernehmen“ ist `Mesh3dquellwechsel` (verwirft die Ergebnisse des Auftrags, startet nichts); danach legt dieser Dienst `koerper.glb` neu an, damit die Mesh-Ansicht SOFORT das neue Netz zeigt und ein
zweiter Schnitt auf dem neuen Netz arbeitet (der Schritt „Netz“ des nächsten Laufs findet die Datei gleich und lässt sie unverändert).
"""

import json
import logging
import os
import re
from pathlib import Path

import numpy as np
from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.blendimportablage import Blendimportablage
from .mesh3deingang import Mesh3deingang
from .mesh3dglbschnitt import Mesh3dglbschnitt
from .mesh3dnetzauswahl import Mesh3dnetzauswahl
from .mesh3dnetzkatalog import Mesh3dnetzkatalog

logger = logging.getLogger('core')

__all__ = ['Mesh3dnetzschnitt']


class Mesh3dnetzschnitt:
    SCHNITTE_MAX = 200
    _FASSUNG = re.compile(r'_bearbeitet_[0-9.]+$')
    _NACH = {}
    _NACH_MAX = 64

    def __init__(self, kennung):
        try:
            self.ablage = Blendimportablage(kennung)
        except ValueError as fehler:
            raise ValueError('Kein Auftrag %s' % kennung) from fehler
        self.stand = self.ablage.stand()
        if not self.stand:
            raise ValueError('Kein Auftrag %s' % kennung)
        self._katalog = None

    @property
    def katalog(self):
        """Erst beim ersten Gebrauch (das Netz zu lesen kostet bei großen Netzen Sekunden) — `ValueError`, wenn es das Netz noch nicht gibt."""
        if self._katalog is None:
            self._katalog = Mesh3dnetzkatalog.fuer(self.ablage)
        return self._katalog

    # ------------------------------------------------------------------ Vorschau

    def maske(self, schnitte):
        """→ `(alle, je_schnitt)`: die entfernten Flächen (F,) bool und die Maske jedes Schnitts."""
        if not isinstance(schnitte, (list, tuple)) or len(schnitte) > self.SCHNITTE_MAX:
            raise ValueError('„schnitte“ muss eine Liste mit höchstens %d Auswahlen sein' % self.SCHNITTE_MAX)
        auswahl = Mesh3dnetzauswahl(self.katalog)
        je = [auswahl.maske(schnitt) for schnitt in schnitte]
        alle = np.zeros(self.katalog.flaechen, dtype=bool)
        for m in je:
            alle |= m
        return alle, je

    def vorschau(self, schnitte):
        """Zahlen zur Auswahl, ohne etwas zu schreiben: je Schnitt und insgesamt Flächen und Anteil, dazu wie viele Teile des Netzes übrig bleiben."""
        alle, je = self.maske(schnitte)
        gesamt = self.katalog.flaechen
        rest = ~alle
        return {'flaechen': gesamt, 'entfernt': int(alle.sum()), 'anteil': round(float(alle.sum()) / gesamt, 5), 'behalten': int(rest.sum()),
                'teile_vorher': int(len(self.katalog.groessen)), 'teile_nachher': int(len(np.unique(self.katalog.insel[rest]))) if rest.any() else 0,
                'schnitte': [{'flaechen': int(m.sum()), 'anteil': round(float(m.sum()) / gesamt, 5)} for m in je]}

    # ------------------------------------------------------------------ Speichern

    def quelle(self):
        datei = Path(str((self.stand.get('quelle') or {}).get('datei') or ''))
        if not datei.is_file() or datei.suffix.lower() != '.glb':
            raise ValueError('Ausschneiden geht nur bei einer GLB-Datei als Quelle (hier: %s)' % (datei.name or 'keine'))
        return datei

    def speichern(self, schnitte, uebernehmen=False):
        """Die neue Datei schreiben (und, bei `uebernehmen`, zur Quelle des Auftrags machen) → Bericht. `ValueError` mit dem Grund."""
        alle, je = self.maske(schnitte)
        entfernt = int(alle.sum())
        if entfernt == 0:
            raise ValueError('Es ist nichts ausgewählt — es gibt nichts zu entfernen')
        if entfernt == len(alle):
            raise ValueError('Die Auswahl umfasst das ganze Netz')
        quelle = self.quelle()
        ziel = self._ziel(quelle)
        vorher, nachher = self._schreiben(quelle, ziel, ~alle)
        bericht = {'datei': str(ziel), 'ordner': str(ziel.parent), 'flaechen_vorher': vorher, 'flaechen_nachher': nachher, 'entfernt': entfernt,
                   'anteil': round(entfernt / vorher, 5), 'groesse_mb': round(ziel.stat().st_size / 1e6, 2), 'uebernommen': False}
        self._begleitdatei(ziel, quelle, schnitte, bericht)
        logger.info('Mesh-3D %s: Netz bearbeitet — %d von %d Flächen entfernt → %s', self.ablage.kennung, entfernt, vorher, ziel)
        if uebernehmen:
            bericht.update(self.uebernehmen(ziel))
        return bericht

    def uebernehmen_datei(self, datei):
        """Eine früher gespeicherte Datei (aus `speichern`) zur Quelle machen: sie muss unter `3DObjects/mesh3d_eingang` liegen und eine GLB sein → wie `uebernehmen`."""
        pfad = Path(str(datei or ''))
        if not pfad.is_file() or pfad.suffix.lower() != '.glb' or not pfad.resolve().is_relative_to(Mesh3deingang.wurzel().resolve()):
            raise ValueError('Nur eine gespeicherte Datei aus dem Eingangsordner kann übernommen werden')
        return self.uebernehmen(pfad)

    def uebernehmen(self, ziel):
        """Die Datei zur Quelle des Auftrags machen → `{uebernommen, verworfen?, grund?}`. Ein laufender Auftrag bleibt unberührt (`grund`)."""
        from .blendimportnetz import Blendimportnetz
        from .mesh3dquellwechsel import Mesh3dquellwechsel

        name = str((self.stand.get('quelle') or {}).get('name') or '').strip()
        try:
            wechsel = Mesh3dquellwechsel(self.ablage.kennung).wechseln(str(ziel), name)
            Blendimportnetz(Blendimportablage(self.ablage.kennung), lambda *_: None).schreiben(ziel)
        except (Mesh3dquellwechsel.Laeuft, ValueError, OSError) as fehler:
            logger.warning('Mesh-3D %s: bearbeitetes Netz nicht übernommen: %s', self.ablage.kennung, fehler)
            return {'uebernommen': False, 'grund': str(fehler)}
        return {'uebernommen': True, 'verworfen': wechsel.get('verworfen'), 'weg': wechsel.get('weg')}

    def vorquelle(self):
        """Die Datei, aus der die jetzige Quelle durch „Netz bearbeiten“ entstand — aus der Begleitdatei `<Name>.json` neben ihr (`_begleitdatei`) → `Path`. `ValueError` mit dem Grund, wenn die Quelle nicht so entstand
        oder die frühere Datei fehlt. Wer die frühere Datei wieder zur Quelle macht, hat den Schnitt zurückgenommen; war sie selbst ein Ergebnis von „Netz bearbeiten“, geht der nächste Schritt zurück genauso."""
        quelle = self.quelle()
        begleit = Path(str(quelle)[:-4] + '.json')
        if not self._FASSUNG.search(quelle.stem) or not begleit.is_file():
            raise ValueError('Die Quelle ist keine mit „Netz bearbeiten“ gespeicherte Datei — es gibt keinen Schnitt zurückzunehmen')
        try:
            vor = Path(str(json.loads(begleit.read_text(encoding='utf-8'))['quelle']['datei']))
        except (OSError, ValueError, KeyError, TypeError) as fehler:
            raise ValueError('Die Begleitdatei %s ist nicht lesbar' % begleit.name) from fehler
        if not vor.is_file() or vor.suffix.lower() != '.glb':
            raise ValueError('Die Datei vor dem Schnitt gibt es nicht mehr (%s)' % vor)
        return vor

    def zurueck(self):
        """Den letzten gespeicherten und übernommenen Schnitt zurücknehmen (14.10.2026, Edgar: „ich brauche auch einen Undo-Button für Löschen“): die Datei VOR dem Schnitt wird wieder Quelle des Auftrags — wie jeder
        Quellwechsel verwirft das die Ergebnisse (`Mesh3dquellwechsel`), gerechnet wird mit „Neu berechnen“. Die bearbeitete Datei bleibt auf der Platte. → wie `uebernehmen`, dazu `datei`."""
        vor = self.vorquelle()
        antwort = self.uebernehmen(vor)
        antwort['datei'] = str(vor)
        return antwort

    @classmethod
    def nachfolger(cls, quelle):
        """Die jüngste mit „Netz bearbeiten“ gespeicherte Datei, die aus `quelle` entstand — nach dem Zurücknehmen eines Schnitts ist das der Schnitt, den man wiederholen kann → `Path` oder `None`.
        Gefunden wird sie über die Begleitdateien (`<Name>_bearbeitet_<Zeit>.json` nennt ihre Quelle, `_begleitdatei`); es gibt keinen zweiten Zustand, der veralten könnte. Eine Suche je Quelle und Stand des
        Eingangsordners wird gemerkt (die Jobseite fragt den Zustand alle paar Sekunden)."""
        quelle = Path(str(quelle or ''))
        wurzel = Mesh3deingang.wurzel()
        try:
            # Stand des Eingangsordners: Zeit UND Zahl der Unterordner — die Zeit allein ändert sich innerhalb eines Zeittakts (~15 ms) nicht, zwei Ordner kurz nacheinander wären ein Stand
            with os.scandir(wurzel) as eintraege:
                marke = (str(quelle), wurzel.stat().st_mtime_ns, sum(1 for _ in eintraege))
            ziel = quelle.resolve()
        except OSError:
            return None
        if marke in cls._NACH:
            gemerkt = cls._NACH[marke]
            return gemerkt if gemerkt is None or gemerkt.is_file() else None
        bester = None
        for begleit in wurzel.glob('*/*/*_bearbeitet_*.json'):
            glb = begleit.with_suffix('.glb')
            try:
                vor = Path(str(json.loads(begleit.read_text(encoding='utf-8'))['quelle']['datei']))
                zeit = begleit.stat().st_mtime_ns
                if not glb.is_file() or vor.resolve() != ziel:
                    continue
            except (OSError, ValueError, KeyError, TypeError):
                continue
            if bester is None or zeit > bester[0]:
                bester = (zeit, glb)
        if len(cls._NACH) > cls._NACH_MAX:
            cls._NACH.clear()
        cls._NACH[marke] = bester[1] if bester else None
        return cls._NACH[marke]

    def wieder(self):
        """Den zurückgenommenen gespeicherten Schnitt wiederholen (14.10.2026, Edgar: „bzw. Strg+Z und Strg+Y“): die jüngste Datei, die aus der jetzigen Quelle entstand, wird wieder Quelle — wie `zurueck` in die andere
        Richtung (Ergebnisse verworfen, gerechnet wird mit „Neu berechnen“). → wie `uebernehmen`, dazu `datei`; `ValueError`, wenn es keinen solchen Schnitt gibt."""
        nach = self.nachfolger(self.quelle())
        if nach is None:
            raise ValueError('Aus dieser Quelle ist kein Schnitt gespeichert worden — es gibt nichts zu wiederholen')
        antwort = self.uebernehmen(nach)
        antwort['datei'] = str(nach)
        return antwort

    # ------------------------------------------------------------------ Hilfen

    def _ziel(self, quelle):
        stamm = self._FASSUNG.sub('', quelle.stem) or quelle.stem
        wurzel = Mesh3deingang.wurzel()
        kennung = Auftragskennung.frei(timezone.now(), lambda k: (wurzel / k).exists())
        ordner = wurzel / kennung / (Mesh3deingang.teile(stamm)[:1] or ['netz'])[0]
        ordner.mkdir(parents=True, exist_ok=True)
        return ordner / ('%s_bearbeitet_%s.glb' % (ordner.name, kennung))

    def _schreiben(self, quelle, ziel, behalten):
        """GLB ohne die nicht behaltenen Flächen, Textur und Material bytegleich (`Mesh3dglbschnitt`) → `(Flächen vorher, nachher)`. Mit trimesh gegengelesen, weil die Pipeline die Datei so liest."""
        import trimesh

        vorher, nachher, _, _ = Mesh3dglbschnitt.schreiben(quelle, ziel, behalten)
        gelesen = trimesh.load(str(ziel), force='scene', process=False)
        if len(gelesen.geometry) != 1 or len(next(iter(gelesen.geometry.values())).faces) != nachher:
            ziel.unlink(missing_ok=True)
            raise ValueError('Die geschriebene Datei hat nicht die erwartete Flächenzahl (%d) — sie wurde wieder gelöscht' % nachher)
        return vorher, nachher

    def _begleitdatei(self, ziel, quelle, schnitte, bericht):
        stand = quelle.stat()
        daten = {'zeit': timezone.localtime().isoformat(timespec='seconds'), 'auftrag': self.ablage.kennung,
                 'quelle': {'datei': str(quelle), 'groesse': stand.st_size, 'geaendert_ns': stand.st_mtime_ns}, 'schnitte': schnitte,
                 **{k: bericht[k] for k in ('flaechen_vorher', 'flaechen_nachher', 'entfernt', 'anteil')}}
        Path(str(ziel)[:-4] + '.json').write_text(json.dumps(daten, indent=2, ensure_ascii=False), encoding='utf-8')
