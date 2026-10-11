# -*- coding: utf-8 -*-
"""Architekturmeshto3d — die Daten des Reiters „MeshTo3D" der Seite Hilfe → Architektur → 2D3D (11.10.2026).

Edgar (11.10.2026): „füge diese Info hinzu in /hilfe/architektur/2d3d/ in neuem Tab - MeshTo3D, wo du alle infos reintust, wie das geht, was von Blender übernommen wurde und so weiter
mit möglichst vielen Details. Auch Klassenmodell, Workflow und so weiter." Der Reiter beschreibt „Mesh to 3D" (Netz → Genesis-9-Figur) und seine Verzahnung mit dem Blender-Import.

Was aus dem Code kommt und was von Hand steht (wie bei den anderen Reitern der Seite): aus dem Code gelesen werden die Schritte und ihre Bänder (`Meshfigurlauf.SCHRITTE`, `BAENDER`), die
Schritte des Imports (`Blendimportlauf.SCHRITTE`), die Optionen (`Meshfiguroptionen.KATALOG`, dazu `Blendimportfigur.OPTIONEN`), jede Klassenkarte (Datei, Zeilen, erster Satz, öffentliche Methoden),
die Importkanten des Klassenmodells und die Zeiten (fertige Aufträge). Von Hand stehen die Beschreibungen (`Architekturmeshto3dschritte`, `…methode`, `…blender`) und die beschrifteten Beziehungen
(`Architekturmeshto3dklassen`). Stimmen Text und Code nicht überein, steht der Befund rot auf der Seite (`befunde`) — und der Test `test_hilfe_architektur_2d3d_meshto3d` wird rot.
"""

import logging

from .architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge
from .architekturmeshto3dblender import Architekturmeshto3dblender
from .architekturmeshto3dklassen import Architekturmeshto3dklassen
from .architekturmeshto3dmethode import Architekturmeshto3dmethode
from .architekturmeshto3dschritte import Architekturmeshto3dschritte
from .architekturmeshto3dzeiten import Architekturmeshto3dzeiten

__all__ = ['Architekturmeshto3d']

logger = logging.getLogger('core')


class Architekturmeshto3d:
    KENNUNG = 'meshto3d'

    @classmethod
    def anker(cls, klasse):
        return 't-%s-%s' % (cls.KENNUNG, klasse)

    @classmethod
    def _links(cls, namen, bekannt, befunde, wo):
        """Klassennamen → [{klasse, anker}]; eine Klasse ohne Karte bekommt keinen Verweis und einen Befund."""
        aus = []
        for name in namen:
            if name not in bekannt:
                befunde.append('%s: %s hat keine Karte im Klassenmodell' % (wo, name))
            aus.append({'klasse': name, 'anker': cls.anker(name) if name in bekannt else ''})
        return aus

    @classmethod
    def schritte(cls, bekannt, befunde):
        """Die Schritte von `Meshfigurlauf` mit ihrem Band und der Beschreibung von Hand."""
        from .meshfigurlauf import Meshfigurlauf

        text = {s[0]: s for s in Architekturmeshto3dschritte.SCHRITTE}
        for name in Meshfigurlauf.SCHRITTE:
            if name not in text:
                befunde.append('Schritt %s steht in Meshfigurlauf.SCHRITTE, aber nicht im Text der Seite' % name)
        for name in text:
            if name not in Meshfigurlauf.SCHRITTE:
                befunde.append('Schritt %s steht im Text der Seite, aber nicht mehr in Meshfigurlauf.SCHRITTE' % name)
        aus = []
        for name in Meshfigurlauf.SCHRITTE:
            _n, welt, k14, k10, was, ergebnis = text.get(name, (name, '?', [], [], 'Nicht beschrieben.', ''))
            von, bis = Meshfigurlauf.BAENDER.get(name, (0, 0))
            aus.append({'schritt': name, 'von': von, 'bis': bis, 'breite': bis - von, 'welt': welt, 'welt_klasse': '14' if welt == 'python14' else 'beide',
                        'was': was, 'ergebnis': ergebnis,
                        'klassen14': cls._links(k14, bekannt, befunde, name), 'klassen10': cls._links(k10, bekannt, befunde, name)})
        return aus

    @staticmethod
    def _werte(eintrag):
        if eintrag['art'] == 'zahl':
            return '%s … %s' % (eintrag['min'], eintrag['max'])
        if eintrag['schluessel'] == 'referenz':
            return 'eine Figur der Genesis-Bibliothek (Testfall)'
        return ' · '.join(str(w) for w, _t in eintrag.get('werte') or [])

    @classmethod
    def optionen(cls):
        """Alle Optionen des Reiters aus dem Katalog des Codes, dazu der Wert, den der Blender-Import setzt."""
        from .blendimportfigur import Blendimportfigur
        from .meshfiguroptionen import Meshfiguroptionen

        aus = []
        for e in Meshfiguroptionen.KATALOG:
            wert = Blendimportfigur.OPTIONEN.get(e['schluessel'], '')
            aus.append({'schluessel': e['schluessel'], 'titel': e['titel'], 'werte': cls._werte(e), 'vorgabe': e['vorgabe'],
                        'fein': bool(e.get('fein')), 'hinweis': e.get('hinweis', ''),
                        'importwert': wert if wert != '' else ('Auswahl im Dialog' if e['schluessel'] == 'basis' else '')})
        return aus

    @classmethod
    def klassen(cls, befunde):
        """Das Klassenmodell: Karten je Gruppe (Datei, Aufgabe, Methoden, ruft / gerufen von) mit den Kanten aus `Architekturmeshto3dklassen`."""
        geprueft = {}
        beziehungen = Architekturmeshto3dklassen.alle_beziehungen()
        karten = Architektur2d3dwerkzeuge.modell(cls.KENNUNG, Architekturmeshto3dklassen.zeilen(), beziehungen, geprueft, befunde)
        je_gruppe = Architekturmeshto3dklassen.gruppe_von()
        gruppen = []
        for kennung, titel, hinweis, _rollen in Architekturmeshto3dklassen.GRUPPEN:
            meine = [k for k in karten if je_gruppe.get(k['klasse'], ('', ''))[0] == kennung]
            gruppen.append({'kennung': kennung, 'titel': titel, 'hinweis': hinweis, 'karten': meine, 'zeilen': sum(k['zeilen'] for k in meine)})
        beschriftet = len(Architekturmeshto3dklassen.BEZIEHUNGEN)
        return {'gruppen': gruppen,
                'zaehlung': {'klassen': len(karten), 'beziehungen': len(beziehungen), 'beschriftet': beschriftet, 'importiert': len(beziehungen) - beschriftet,
                             'zeilen': sum(k['zeilen'] for k in karten)}}

    @classmethod
    def blender(cls, befunde):
        """Die Schritte des Imports (Blender ja / nein / Option) gegen `Blendimportlauf.SCHRITTE` gehalten, dazu die Tabellen der Übernahme."""
        from .blendimportlauf import Blendimportlauf

        text = {s[0] for s in Architekturmeshto3dblender.IMPORT_SCHRITTE}
        for name in Blendimportlauf.SCHRITTE:
            if name not in text:
                befunde.append('Import-Schritt %s steht in Blendimportlauf.SCHRITTE, aber nicht im Text der Seite' % name)
        for name in text - set(Blendimportlauf.SCHRITTE):
            befunde.append('Import-Schritt %s steht im Text der Seite, aber nicht mehr in Blendimportlauf.SCHRITTE' % name)
        b = Architekturmeshto3dblender
        schritte = [{'schritt': s, 'blender': j, 'was': w, 'klassen': k} for s, j, w, k in b.IMPORT_SCHRITTE]
        return {'schritte': schritte, 'belege': b.BELEGE, 'uebernahmen': b.UEBERNAHMEN, 'messung': b.MESSUNG, 'offen': b.OFFEN,
                'verzahnung': b.IMPORT_VERZAHNUNG, 'anderswo': b.ANDERSWO,
                'zaehlung': {'ja': sum(1 for s in schritte if s['blender'] == 'ja'), 'option': sum(1 for s in schritte if s['blender'] == 'Option'),
                             'nein': sum(1 for s in schritte if s['blender'] == 'nein')}}

    @classmethod
    def _rein(cls, wert):
        """Markdown-Zeichen (Rückstriche) aus allen Texten nehmen — die Seite zeigt sie sonst wörtlich (wie `Architektur2d3dklassen.satz`)."""
        if isinstance(wert, str):
            return wert.replace('`', '')
        if isinstance(wert, dict):
            return {k: cls._rein(v) for k, v in wert.items()}
        if isinstance(wert, (list, tuple)):
            return type(wert)(cls._rein(v) for v in wert)
        return wert

    @classmethod
    def kontext(cls):
        return cls._rein(cls._bauen())

    @classmethod
    def _bauen(cls):
        befunde = []
        klassen = cls.klassen(befunde)
        bekannt = set(Architekturmeshto3dklassen.gruppe_von())
        schritte = cls.schritte(bekannt, befunde)
        s = Architekturmeshto3dschritte
        return {
            'stand': s.STAND,
            'kurz': [{'titel': t, 'text': x} for t, x in s.KURZ],
            'schritte': schritte,
            'dateien': [{'datei': d, 'schreibt': w, 'liest': r, 'inhalt': i} for d, w, r, i in s.DATEIEN],
            'zeiten': dict(Architekturmeshto3dzeiten.lesen([x['schritt'] for x in schritte]), spalten=[x['schritt'] for x in schritte]),
            'optionen': cls.optionen(),
            'methode': [{'titel': t, 'punkte': p} for t, p in Architekturmeshto3dmethode.METHODE],
            'grenzen': [{'was': w, 'befund': b} for w, b in Architekturmeshto3dmethode.GRENZEN],
            'klassen': klassen,
            'blender': cls.blender(befunde),
            'befunde': befunde,
        }
