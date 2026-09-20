# -*- coding: utf-8 -*-
"""Bildmodellfotolinien — je Hauptbild die Maßlinien darauf, für die Tabelle der Proportionen.

Edgar (19.09.2026, abends): „eine Tabelle mit Bildern, Spalten: Bild, Button
Löschen, Button Ersetzen, Bild vorher, Bild nachher. Ein Bild pro Zeile,
Popup auf dem Bild gibt die Maße an … auch die Position verschieben."

Jedes Hauptbild des Auftrags (Körper vorn/Seite/hinten/dreiviertel, Kopf
vorn/Seite; kein Video, für die Form gezählt) bekommt einen Eintrag: seine
Ansicht der Proportionen (`vorn`, `seite`, `hinten`, `kopf` — oder None, wo
es keine Linien gibt), die Linien der 19 Maße in seinen Pixeln
(`G9fotolinien`, Startlagen aus Profil und Rig) und den Maßstab `px_je_m`.
Hat Edgar Linien im Popup gezogen, liegen sie unter
`optionen.proportionen_linien[datei] = {linien, entfernt}` und ersetzen die Startlagen
dieses Bildes; `entfernt` nennt die Maße, deren Marker er aus DIESEM Bild gelöscht hat
(20.09.2026: „ich möchte einzelne Marker LÖSCHEN können aus den Popups") — sie
bekommen keine Linie mehr. Die Ausgabe hängt am Zustand (`fotolinien`), damit die Seite sie
ohne Lauf hat; sie kostet nur das Glätten der Profile (0,07 s für elf Bilder).
"""

import logging

from .bildmodellbildtypen import Bildmodellbildtypen

logger = logging.getLogger('core')

__all__ = ['Bildmodellfotolinien']


class Bildmodellfotolinien:
    #: (Kategorie, Ansicht des Bildes) → Ansicht der Proportionen.
    ANSICHT = {('koerper', 'vorne'): 'vorn', ('koerper', 'seite'): 'seite',
               ('koerper', 'hinten'): 'hinten', ('kopf', 'vorne'): 'kopf'}
    #: Reihenfolge der Zeilen: Körper vorn, Seite, hinten, dreiviertel, dann Kopf.
    REIHE = ['koerper/vorne', 'koerper/seite', 'koerper/hinten', 'koerper/dreiviertel',
             'kopf/vorne', 'kopf/seite', 'kopf/hinten']
    OPTION = 'proportionen_linien'

    def __init__(self, job):
        self.job = job
        self.bilder = job.bilder or []
        self.optionen = job.optionen or {}
        self.ergebnis = job.ergebnis or {}

    # -------------------------------------------------------------- Wahl

    def hauptbilder(self):
        """Die Bilder der Tabelle, in Zeilenreihenfolge: erst die von Hand nummerierten
        (`reihe`, Spalte „Nr." — Edgar, 20.09.2026: „Wenn ich die Zahl ändere, dann
        ändert sich die Reihenfolge der Bilder gleich"), dann die übrigen nach Typ."""
        aus = [b for b in self.bilder if b.get('kategorie') in ('koerper', 'kopf') and not b.get('video')
               and Bildmodellbildtypen.fuer_form(b)]

        def rang(b):
            typ = '%s/%s' % (b.get('kategorie'), b.get('ansicht'))
            i = self.REIHE.index(typ) if typ in self.REIHE else len(self.REIHE)
            reihe = b.get('reihe')
            return (int(reihe) if isinstance(reihe, int) and reihe > 0 else 10 ** 6,
                    i, b.get('haltung') != 'neutral', -float(b.get('gewicht') or 0), b.get('datei') or '')

        return sorted(aus, key=rang)

    def reihenfolge(self, dateien):
        """Die Zeilen in dieser Reihenfolge nummerieren (`reihe` 1..n); unbekannte Namen
        zählen nicht, nicht genannte Bilder verlieren ihre Nummer. Gibt die Nummern zurück."""
        bekannt = {b.get('datei'): b for b in self.bilder}
        aus = {}
        for datei in dateien if isinstance(dateien, (list, tuple)) else []:
            b = bekannt.get(str(datei))
            if b is not None and str(datei) not in aus:
                aus[str(datei)] = len(aus) + 1
        for b in self.bilder:
            if b.get('datei') in aus:
                b['reihe'] = aus[b['datei']]
            else:
                b.pop('reihe', None)
        return aus

    def ziel_m(self):
        """Die Zielmaße in Metern — Eingaben vor den gemessenen Zielen (für Arme und den Kopfmaßstab)."""
        ziel = dict((self.ergebnis.get('proportionen') or {}).get('ziel') or {})
        ziel.update({k: v for k, v in (self.optionen.get('proportionen') or {}).items() if v is not None})
        return {k: float(v) / 100.0 for k, v in ziel.items() if v is not None}

    def hoehe_m(self):
        h = ((self.ergebnis.get('ziel') or {}).get('hoehe_ziel_cm')
             or (self.optionen.get('person') or {}).get('groesse_cm'))
        return float(h) / 100.0 if h else None

    # ------------------------------------------------------------ Linien

    def alle(self):
        """`[{datei, ansicht, kategorie, blick, breite, hoehe, px_je_m, linien}]` je Hauptbild, in Reihe."""
        from Genesis9.fotolinien import G9fotolinien

        ziel = self.ziel_m()
        hoehe = self.hoehe_m()
        gemerkt = self.optionen.get(self.OPTION) or {}
        aus = []
        for b in self.hauptbilder():
            ansicht = self.ANSICHT.get((b.get('kategorie'), b.get('ansicht')))
            px_je_m, linien = None, {}
            if ansicht:
                try:
                    g = G9fotolinien(b, ziel)
                    px_je_m, linien = g.kopf() if ansicht == 'kopf' else g.koerper(hoehe)
                except Exception as fehler:  # stumm gewollt: ein kaputter Eintrag kostet nur seine Linien
                    logger.warning('Bildmodell %s: Fotolinien %s: %s', self.job.kennung, b.get('datei'),
                                   fehler)
            eigenes = gemerkt.get(b.get('datei')) or {}
            eigene = eigenes.get('linien') or {}
            linien = dict(linien, **{k: v for k, v in eigene.items() if self.linie_ok(v)})
            entfernt = [k for k in (eigenes.get('entfernt') or []) if k in linien]
            for k in entfernt:
                linien.pop(k, None)
            aus.append({'datei': b['datei'], 'ansicht': ansicht, 'kategorie': b.get('kategorie'),
                        'blick': b.get('ansicht'), 'breite': b.get('breite'), 'hoehe': b.get('hoehe'),
                        'px_je_m': px_je_m, 'linien': linien, 'entfernt': entfernt,
                        'reihe': len(aus) + 1})
        return aus

    @staticmethod
    def linie_ok(v):
        try:
            return (isinstance(v, (list, tuple)) and len(v) == 2
                    and all(len(p) == 2 and all(isinstance(float(c), float) for c in p) for p in v))
        except (TypeError, ValueError):
            return False

    @classmethod
    def linien_pruefen(cls, roh):
        """`{datei: {linien: {schluessel: [[x, y], [x, y]]}, entfernt: [schluessel]}}` —
        bekannte Maße, runde Pixel; ein entferntes Maß hat keine Linie."""
        from Genesis9.proportionen import G9proportionen

        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for datei, eintrag in roh.items():
            if not datei or not isinstance(eintrag, dict):
                continue
            weg = eintrag.get('entfernt')
            entfernt = sorted({str(k) for k in weg if str(k) in G9proportionen.NAMEN}
                              if isinstance(weg, (list, tuple)) else set())
            linien = {}
            for k, v in (eintrag.get('linien') or {}).items():
                if k in G9proportionen.NAMEN and k not in entfernt and cls.linie_ok(v):
                    linien[k] = [[round(float(v[0][0]), 1), round(float(v[0][1]), 1)],
                                 [round(float(v[1][0]), 1), round(float(v[1][1]), 1)]]
            if linien or entfernt:
                aus[str(datei)] = {'linien': linien}
                if entfernt:
                    aus[str(datei)]['entfernt'] = entfernt
        return aus
