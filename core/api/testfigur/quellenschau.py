# -*- coding: utf-8 -*-
"""Quellenschau — was in der Testfassung liegt, für die Testseite aufbereitet.

Aus `core/test_character_api.py` herausgelöst (17.08.2026). `test_character_source`
war eine Funktion mit 117 Zeilen und sechs aneinandergereihten Abschnitten
(Quelldateien, L1-Morphs, Geschlechtsdelta, L2-Pakete, Datendateien,
CharMorph-Referenz) — jeder mit eigenem `try`, eigenem Fehlertext und derselben
Verzeichnisschleife. Jetzt eine Methode je Abschnitt.

DER FEHLERTEXT GEHÖRT HIER IN DIE ANTWORT und nicht ins Log: Diese Seite zeigt
den Zustand der Testdaten. „Datei X nicht lesbar" ist ihr Ergebnis, kein
Zwischenfall.
"""

import json
import logging
import os

import numpy as np

from .testkern import Testkern

logger = logging.getLogger(__name__)


class Quellenschau:
    """Sammelt Quelltext und Datenbestand der Testfassung."""

    #: Wie viele Morphnamen je L2-Paket in die Antwort gehen — die Liste ist zum
    #: Hineinsehen da, nicht zum Auflisten von Tausenden.
    NAMEN_JE_PAKET = 20

    def __init__(self):
        self.quellordner = os.path.join(Testkern.WURZEL, 'humanbody_core')

    @property
    def vorhanden(self):
        return os.path.isdir(self.quellordner)

    def bericht(self):
        # Dictionary gewollt: geht unveraendert als JSON an die Testseite.
        return {
            'files': self.quelldateien(),
            'charmorph_files': self.referenzdateien(),
            'data_diagnostics': {
                'l1': self.l1_morphs(),
                'gender_delta': self.geschlechtsdelta(),
                'l2_packed': self.l2_pakete(),
                'data_files': self.datendateien(),
            },
        }

    # ------------------------------------------------------------- Quelldateien

    def quelldateien(self):
        return self._texte(self.quellordner)

    def referenzdateien(self):
        return self._texte(Testkern.CHARMORPH_REF)

    @staticmethod
    def _texte(ordner):
        """Alle `.py`-Dateien eines Ordners mit ihrem Inhalt."""
        if not os.path.isdir(ordner):
            return []
        aus = []
        for name in sorted(os.listdir(ordner)):
            if not name.endswith('.py'):
                continue
            pfad = os.path.join(ordner, name)
            try:
                with open(pfad, 'r', encoding='utf-8') as f:
                    aus.append({'name': name, 'content': f.read()})
            # stumm gewollt: Der Fehlertext IST das Ergebnis dieser Seite,
            # siehe Modulkopf.
            except OSError as e:
                aus.append({'name': name, 'content': '# Nicht lesbar: %s' % e})
        return aus

    # ---------------------------------------------------------------- Morphdaten

    def l1_morphs(self):
        """Je L1-Datei: Größe, Form, Punktzahl, Datentyp."""
        ordner = Testkern.datei('morphs', 'L1')
        if not os.path.isdir(ordner):
            return []
        aus = []
        for name in sorted(os.listdir(ordner)):
            if not name.endswith('.npy'):
                continue
            pfad = os.path.join(ordner, name)
            eintrag = {'name': name[:-4], 'file': name,
                       'size_bytes': os.path.getsize(pfad)}
            eintrag.update(self._feldform(pfad))
            aus.append(eintrag)
        return aus

    def geschlechtsdelta(self):
        """Das Delta zwischen den Geschlechtern — eine einzelne Datei."""
        pfad = Testkern.datei('morphs', 'gender_male.npy')
        if not os.path.isfile(pfad):
            return None
        eintrag = {'file': 'gender_male.npy',
                   'size_bytes': os.path.getsize(pfad)}
        eintrag.update(self._feldform(pfad))
        return eintrag

    @staticmethod
    def _feldform(pfad):
        """Form und Typ eines `.npy` — oder der Grund, warum nicht."""
        try:
            feld = np.load(pfad)
        # stumm gewollt: Der Fehlertext IST das Ergebnis dieser Seite.
        except (OSError, ValueError) as e:
            return {'error': str(e)}
        return {'shape': list(feld.shape), 'vertex_count': int(feld.shape[0]),
                'dtype': str(feld.dtype)}

    def l2_pakete(self):
        """Je L2-Paket: Anzahl und die ersten Namen."""
        ordner = Testkern.datei('morphs', 'L2_packed')
        if not os.path.isdir(ordner):
            return []
        aus = []
        for name in sorted(os.listdir(ordner)):
            if name.endswith('.npz'):
                aus.append(self._paket(os.path.join(ordner, name), name))
        return aus

    def _paket(self, pfad, name):
        eintrag = {'file': name, 'size_bytes': os.path.getsize(pfad)}
        try:
            with np.load(pfad) as paket:
                namen = [n.decode('utf-8')
                         for n in bytes(paket['names']).split(b'\0')]
        # stumm gewollt: Der Fehlertext IST das Ergebnis dieser Seite.
        except (OSError, ValueError, KeyError) as e:
            eintrag['error'] = str(e)
            return eintrag
        eintrag['morph_count'] = len(namen)
        eintrag['morph_names'] = namen[:self.NAMEN_JE_PAKET]
        return eintrag

    @staticmethod
    def datendateien():
        """Die Dateien direkt im Datenordner, nur Name und Größe."""
        ordner = Testkern.datenordner()
        if not os.path.isdir(ordner):
            return []
        aus = []
        for name in sorted(os.listdir(ordner)):
            pfad = os.path.join(ordner, name)
            if os.path.isfile(pfad):
                aus.append({'name': name, 'size_bytes': os.path.getsize(pfad)})
        return aus

    # ------------------------------------------------------------ Fassungsinfo

    @staticmethod
    def fassung():
        """`commit_info.json` der geladenen Fassung — oder None."""
        pfad = os.path.join(Testkern.WURZEL, 'commit_info.json')
        if not os.path.isfile(pfad):
            return None
        with open(pfad, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def fassung_schreiben(daten):
        pfad = os.path.join(Testkern.WURZEL, 'commit_info.json')
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)
