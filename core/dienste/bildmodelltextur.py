# -*- coding: utf-8 -*-
"""Bildmodelltextur — welche Bilder die Haut liefern und welcher Ton daraus wird.

Edgar (19.09.2026): „Überlege auch ob eine Textur möglich wäre … welches Bild
für die Textur genutzt werden könnte und welches nicht, und wie sich dann
interaktiv die Textur / das Modell verändert, wenn ich eine Textur anwähle /
abwähle."

Stufe 1: Die Sichtung misst je Ausschnitt Hautton, Hautanteil und
Maskenhöhe (`hauttonprobe.py`, YOLO11-Seg + YCrCb-Hautschwelle) und sagt,
ob das Bild taugt (Hauptbild, Haut ≥ 25 % der Maske, Maske ≥ 400 px).
Die Kachel zeigt Farbfeld und Häkchen; `textur_an` ist die Wahl des
Nutzers (Vorgabe = tauglich). `hautton(bilder)` mischt die gewählten
Bilder nach Hautpixeln (Anteil × Maskenhöhe) — der Zustand trägt das
Ergebnis, die 3D-Ansicht tönt die Daz-Haut damit (Faktor gegen den
mittleren Ton der Albedo, `ansicht3d.js`). Beleg an Damira: Vorderansicht
(187, 132, 103), Kopfbild (176, 129, 102), posiertes Bild im Gegenlicht
(121, 93, 74) — darum die Wahl je Bild.

Stufe 2 (Vorschlag): Farbe je Käfigpunkt über die SMPL-X-Projektion des
jeweiligen Bildes (Pose und Kamera sind exakt, `netzabweichung_mm` 0,0)
und die Netzpaarung, gewichtet nach Blickwinkel (Normale · Kamera) und
Auflösung (px je cm), sichtbar nur, was die Personenmaske deckt und
nichts davor liegt (Tiefenprobe); dann je UDIM-Kachel als Textur gebacken
und über die Daz-Haut gelegt. Aufwand: ein Runner (python10), ein
Backschritt (python14), die Ansicht (`vertexColors` sofort, Textur nach).
"""

import numpy as np

__all__ = ['Bildmodelltextur']


class Bildmodelltextur:
    @classmethod
    def gewaehlt(cls, bild):
        """Zählt das Bild zur Textur? Nutzung (nicht „nur Form"/„aus"), dann die
        Nutzerwahl, sonst die Tauglichkeit — ein Nebenbild mit Körperteil
        (`Bildmodellbildtypen`, 19.09.2026) gilt mit Hautton als gewählt.

        Nie gewählt, was `liste` als unmöglich führt (Gruppenbild, ohne Befund, Nebenbild
        ohne Körperteil): sonst steht das Häkchen an UND gesperrt, und niemand kommt mehr
        heran (Edgar, 20.09.2026: „kann sie nicht unchecken" — drei Körperbilder, per Box
        zum Nebenbild gemacht, blieben als tauglich gewählt)."""
        from .bildmodellbildtypen import Bildmodellbildtypen

        t = bild.get('textur') or {}
        if not t.get('hautton') or not Bildmodellbildtypen.fuer_textur(bild):
            return False
        kategorie = bild.get('kategorie') or 'neben'
        if kategorie in ('gruppe', 'leer'):
            return False
        if kategorie == 'neben' and not Bildmodellbildtypen.textur_teile(bild):
            return False
        if 'textur_an' in bild:
            return bool(bild['textur_an'])
        return cls.tauglich(bild) or bool(Bildmodellbildtypen.textur_teile(bild))

    #: Wie `Hauttonprobe.ANTEIL_AB`/`MASKE_AB`: die Tauglichkeit eines Hauptbilds, hier neu
    #: gerechnet — die Sichtung schrieb `tauglich: False, kein Hauptbild`, als das Bild noch
    #: Nebenbild war; wer es per Box zum Hauptbild macht, soll es in der Textur haben.
    ANTEIL_AB = 0.25
    MASKE_AB = 400

    @classmethod
    def tauglich(cls, bild):
        """Taugt das Bild von sich aus für die Textur (Hauptbild mit genug Haut)?"""
        from .bildmodellbildtypen import Bildmodellbildtypen

        t = bild.get('textur') or {}
        if not t.get('hautton'):
            return False
        if bild.get('kategorie') not in Bildmodellbildtypen.HAUPTKATEGORIEN or 'anteil' not in t:
            return bool(t.get('tauglich'))
        return float(t.get('anteil') or 0) >= cls.ANTEIL_AB and int(t.get('maske_px') or 0) >= cls.MASKE_AB

    @classmethod
    def hautton(cls, bilder):
        """`{hautton: [r, g, b], bilder: n, tauglich: m}` — gemischt nach Hautpixeln."""
        summe = np.zeros(3)
        gewicht = 0.0
        n = 0
        tauglich = 0
        for b in bilder:
            t = b.get('textur') or {}
            if cls.tauglich(b):
                tauglich += 1
            if not cls.gewaehlt(b):
                continue
            w = float(t.get('anteil') or 0) * float(t.get('maske_px') or 0)
            if w <= 0:
                continue
            summe += np.asarray(t['hautton'], dtype=float) * w
            gewicht += w
            n += 1
        if gewicht <= 0:
            return {'hautton': None, 'bilder': 0, 'tauglich': tauglich}
        return {'hautton': [int(round(v)) for v in summe / gewicht], 'bilder': n, 'tauglich': tauglich}

    @staticmethod
    def reihenfolge(bilder, dateien):
        """Die Zeilen der Texturtabelle in dieser Reihe nummerieren (`textur_reihe` 1..n) — wie
        `Bildmodellfotolinien.reihenfolge` für die Proportionentabelle (Edgar, 20.09.2026: „ändere
        ich die Zahl, wird das Bild sofort verschoben"). Gibt die Nummern zurück."""
        bekannt = {b.get('datei'): b for b in bilder}
        aus = {}
        for d in dateien if isinstance(dateien, (list, tuple)) else []:
            if bekannt.get(str(d)) is not None and str(d) not in aus:
                aus[str(d)] = len(aus) + 1
        for b in bilder:
            if b.get('datei') in aus:
                b['textur_reihe'] = aus[b['datei']]
            else:
                b.pop('textur_reihe', None)
        return aus

    @staticmethod
    def _reihe(b):
        r = b.get('textur_reihe')
        return int(r) if isinstance(r, int) and r > 0 else 10 ** 6

    @classmethod
    def liste(cls, bilder):
        """Für den Bereich „Textur" der Seite (19.09.2026): je Bild, ob es zur Textur
        zählt, warum nicht, und wie es projiziert wird (Kamera bekannt oder aus dem Rig) —
        in der Reihe der Spalte „Nr." (`textur_reihe`), sonst wie im Auftrag."""
        from .bildmodellbildtypen import Bildmodellbildtypen

        aus = []
        for b in sorted(bilder, key=cls._reihe):
            if b.get('video'):
                continue
            t = b.get('textur') or {}
            kategorie = b.get('kategorie') or 'neben'
            teile = Bildmodellbildtypen.textur_teile(b)
            grund = ''
            if not Bildmodellbildtypen.fuer_textur(b):
                grund = 'Nutzung: %s' % dict((w, a) for w, a, _ in Bildmodellbildtypen.NUTZUNG)[
                    Bildmodellbildtypen.nutzung(b)]
            elif not t.get('hautton'):
                grund = 'keine Hautprobe — noch nicht gesichtet'
            elif kategorie in ('gruppe', 'leer'):
                grund = 'Gruppenbild oder ohne Befund'
            elif kategorie == 'neben' and not teile:
                grund = 'Nebenbild ohne Körperteil — Typ wählen'
            rig = (any((b.get('rigs') or {}).values()) or bool(b.get('gesicht68'))
                   or bool(b.get('haende_punkte')))
            kamera = 'bekannt' if b.get('kamera_bekannt') else ('rig' if rig else 'keine')
            aus.append({
                'datei': b['datei'],
                'reihe': b.get('textur_reihe'),
                'kategorie': kategorie,
                'ansicht': b.get('ansicht'),
                'teil': b.get('teil'),
                'nutzung': Bildmodellbildtypen.nutzung(b),
                'hautton': t.get('hautton'),
                'gewaehlt': cls.gewaehlt(b),
                'moeglich': not grund,
                'grund': grund,
                'kamera': kamera,
                'breite': b.get('breite'),
                'hoehe': b.get('hoehe'),
            })
        return aus

    # ------------------------------------------------------------- Referenz

    #: Hautgruppe der Daz-Figur → UDIM-Kachel (Genesis 9; Nägel teilen 1005).
    GRUPPENKACHEL = {'Head': 1001, 'Body': 1002, 'Legs': 1003, 'Arms': 1004, 'Fingernails': 1005}

    @classmethod
    def referenz(cls, optionen, ergebnis=None):
        """`{name, kacheln: {kachel: Bibliothekspfad}}` — zum Vergleich unter den gebackenen
        Kacheln: die TATSÄCHLICHE Haut der Referenzfigur eines Testfalls (Edgar, 20.09.2026:
        „mach einen Bereich mit der tatsächlichen Textur von Ursula darunter, damit ich
        vergleichen kann"), sonst die Standard-Genesis-Haut nach dem Geschlecht der
        Anpassung (`ergebnis.anpassung.basis`; Edgar an websites-02: Damira ist kein
        Testfall). Die Seite holt die Bilder über `Genesis9texturen.ADRESSE`."""
        from Genesis9.charaktere import G9charaktere

        from .bildmodelltestfall import Bildmodelltestfall

        name = Bildmodelltestfall.figur(optionen)
        eintrag = G9charaktere.eintrag(name) if name else None
        if eintrag:
            titel = 'Referenzfigur %s (Daz-Albedo, dieselben Kacheln)' % (eintrag.get('anzeige') or name)
        else:
            basis = ((ergebnis or {}).get('anpassung') or {}).get('basis') or 'feminine'
            maennlich = str(basis).lower().startswith('masc')
            eintrag = {'haut': G9charaktere.HAUT_M if maennlich else G9charaktere.HAUT_W}
            titel = 'Standard-Genesis-Textur (Base %s)' % ('Masculine' if maennlich else 'Feminine')
        bilder = G9charaktere.hautbilder(eintrag) or {}
        kacheln = {}
        for gruppe, kachel in cls.GRUPPENKACHEL.items():
            albedo = (bilder.get(gruppe) or {}).get('albedo')
            if albedo:
                kacheln[str(kachel)] = str(albedo).replace('\\', '/')
        return {'name': titel, 'kacheln': kacheln} if kacheln else {}
