# -*- coding: utf-8 -*-
"""Modellexportziel — Ordner und Dateinamen fuer den Modell-Export.

ANDERES SICHERHEITSMODELL ALS `SafePath` (26.09.2026)
======================================================
`SafePath` prueft, ob ein Pfad innerhalb bekannter Projektwurzeln liegt —
richtig fuer Studio-Projekte und Video-Ausgabe, wo der Nutzer aus wenigen
EINGESTELLTEN Ordnern waehlt. Der Modell-Export soll dagegen in JEDEN Ordner
schreiben duerfen (Edgar, 26.09.2026: „Ordnerwahl: jeder beliebige Ordner") —
ein Export nach `D:\\Roomguest\\Assets` oder auf einen USB-Stick ist ein
gewollter Anwendungsfall, keine Ausnahme, die man zulassen muesste.

Was bleibt, ist die engere Pruefung: keine Netzwerk-/Datenstrompfade, keine
Windows-Gerätenamen als Ordner- oder Dateiname — UND die Projektregel
(`~/.claude/CLAUDE.md`: „NIE in HumanBody/data/ oder HumanBodyBlender/data/
schreiben") bleibt hart verdrahtet, unabhaengig davon, was der Nutzer eintippt.
"""

import logging
import os
import re
from pathlib import Path

from django.conf import settings

from ..daten.pfadvergleich import Pfadvergleich
from ..namensregeln import Namensregeln

logger = logging.getLogger('core')


class ZielAbgelehnt(ValueError):
    """Ordner oder Name sind nicht zulässig — der Text geht an den Browser."""


class Modellexportziel:
    """Ein geprüfter Ordner (angelegt) + ein eindeutiger Dateistamm."""

    @staticmethod
    def _gesperrte_ordner():
        """Unter diesen beiden liegen Morphs, Netze, Gewichte — Projektregel."""
        wurzel = Path(str(settings.TOOLS_ROOT))
        return [wurzel / 'HumanBody' / 'data', wurzel / 'HumanBodyBlender' / 'data']

    @staticmethod
    def ordner(roh):
        """Der geprüfte, angelegte Zielordner — oder `ZielAbgelehnt`.

        Dieselben zwei Grobprüfungen wie in `SafePath._grobpruefung` (UNC,
        NTFS-Datenströme) — hier eigenständig, weil das Wurzelmodell darunter
        ein anderes ist (siehe Moduldocstring).
        """
        text = (str(roh) if roh is not None else '').strip()
        if not text:
            raise ZielAbgelehnt('Kein Ordner angegeben')
        if text.startswith('\\\\') or text.startswith('//'):
            raise ZielAbgelehnt('Netzwerkpfade sind nicht erlaubt')
        ohne_laufwerk = text[2:] if len(text) > 1 and text[1] == ':' else text
        if ':' in ohne_laufwerk:
            raise ZielAbgelehnt('Doppelpunkte im Pfad sind nicht erlaubt')
        try:
            ziel = Path(text).resolve()
        except (OSError, ValueError) as e:
            raise ZielAbgelehnt('Pfad nicht auflösbar: %s' % e) from e
        if not ziel.is_absolute():
            raise ZielAbgelehnt('Der Ordner muss ein absoluter Pfad sein')
        for teil in ziel.parts[1:]:
            grund = Namensregeln.geraet(teil, 'Ordnername') or Namensregeln.zeichen(teil, 'Ordnername')
            if grund:
                raise ZielAbgelehnt(grund)
        for gesperrt in Modellexportziel._gesperrte_ordner():
            if Pfadvergleich.liegt_unter(ziel, gesperrt):
                raise ZielAbgelehnt(
                    '%s ist ein Produktivdaten-Ordner und für den Export gesperrt' % gesperrt
                )
        try:
            os.makedirs(ziel, exist_ok=True)
        except OSError as e:
            raise ZielAbgelehnt('Ordner nicht anlegbar: %s' % e) from e
        return ziel

    @staticmethod
    def name(roh, ersatz='figur'):
        """Bereinigter Namensstamm — dieselbe Positivliste wie `Speichernmenue`
        und `Stoffexportziel`: Buchstaben, Ziffern, Leerzeichen, Binde- und
        Unterstriche."""
        text = str(roh or '').strip()
        sauber = re.sub(r'[^\w\s\-]', '', text).strip()
        return sauber or ersatz

    @staticmethod
    def eindeutiger_stamm(ordner, stamm, endungen):
        """`stamm`, oder `stamm_2`, `stamm_3`, … — solange KEINE der `endungen`
        (mit Punkt, z. B. `.glb`) unter diesem Stamm schon existiert.

        Alle Dateien EINES Exports (GLB, MTL, Bildkarten, …) teilen sich
        denselben Stamm und damit denselben Zähler — sonst zeigt eine MTL-Datei
        am Ende auf ein PNG mit einem anderen Namen, weil nur die MTL kollidierte.
        Kein stilles Überschreiben (Projektregel „Ablagen brauchen einen
        Fassungsnamen" — hier gibt es keine Fassung, also einen Zähler).
        """
        kandidat = stamm
        zaehler = 2
        while any((Path(ordner) / (kandidat + e)).exists() for e in endungen):
            kandidat = '%s_%d' % (stamm, zaehler)
            zaehler += 1
        return kandidat
